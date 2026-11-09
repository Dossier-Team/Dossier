"""The audio bridge between a Twilio media socket and a Deepgram voice agent.

This is where the call actually happens: Twilio's mulaw frames go up to
Deepgram, Deepgram's synthesized audio comes back down, and the transcript
accumulates on the session as it goes. Deepgram has no post-call webhook — the
transcript exists only here, so whatever is on the session when this returns is
all the extraction step will ever see.
"""

import asyncio
import logging
from dataclasses import dataclass, field

from deepgram.agent.v1.socket_client import AsyncV1SocketClient
from fastapi import WebSocket

from src.agent.session import CallSession
from src.agent.settings import build_agent_settings
from src.clients import TWILIO_AUTH_TOKEN, dg_client
from src.telephony import twilio_protocol as twilio
from src.telephony.security import is_valid_stream_token

logger = logging.getLogger(__name__)

# Deepgram closes an idle agent socket, so it gets a keepalive through long silences.
KEEPALIVE_SECONDS = 5.0

# Deepgram sends speech faster than it plays, so a pause this long means the goodbye is all sent.
AUDIO_QUIET_SECONDS = 1.0
# If no audio follows the goodbye's text within this long, assume the audio came first.
CLOSING_AUDIO_WAIT_SECONDS = 3.0
# Hang up regardless this long after the goodbye.
HANGUP_TIMEOUT_SECONDS = 25.0
HANGUP_POLL_SECONDS = 0.2
HANGUP_MARK = "hangup"

# Deepgram reports these several times a second; they'd drown out the rest of the debug log.
_QUIET_EVENTS = {"LatencyReport", "History", "AgentThinking"}


class StreamRejected(Exception):
    """The media stream didn't carry a token from our inbound-call webhook."""


@dataclass
class _Hangup:
    """Hanging up once the agent's goodbye has finished playing, not while it's still being said.

    Each hangup mark is named after how many audio chunks had been sent when it
    was sent. Twilio echoes a mark once the audio before it has played, so an
    echo means "hang up now" only if no audio was sent after that mark.
    """

    goodbye_at: float | None = None
    audio_chunks: int = 0
    last_audio_at: float = 0.0
    done: asyncio.Event = field(default_factory=asyncio.Event)
    timer: asyncio.Task | None = None


async def run_bridge(twilio_ws: WebSocket, session: CallSession) -> None:
    """Run the call to completion, filling in `session` as it goes.

    Returns when either side hangs up or the agent says goodbye; raises
    `StreamRejected` for a stream we didn't start, and whatever the losing task
    raised (`WebSocketDisconnect` on a normal caller hangup).
    """
    parameters = await _wait_for_start(twilio_ws, session)
    if parameters is None:
        return
    if not is_valid_stream_token(TWILIO_AUTH_TOKEN, session.call_sid, parameters.get("token")):
        raise StreamRejected(f"No valid stream token for call {session.call_sid}")

    hangup = _Hangup()
    async with dg_client.agent.v1.connect() as agent:
        await agent.send_settings(build_agent_settings(session))
        tasks = [
            asyncio.create_task(_twilio_to_agent(twilio_ws, agent, hangup)),
            asyncio.create_task(_agent_to_twilio(twilio_ws, agent, session, hangup)),
            asyncio.create_task(_keepalive(agent)),
            asyncio.create_task(hangup.done.wait()),
        ]
        try:
            done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                task.result()
        finally:
            if hangup.timer is not None:
                tasks.append(hangup.timer)
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)


async def _wait_for_start(twilio_ws: WebSocket, session: CallSession) -> dict[str, str] | None:
    """Twilio sends `connected`, then `start` with the call's details, before any audio."""
    async for raw in twilio_ws.iter_text():
        frame = twilio.decode_frame(raw)
        event = twilio.frame_event(frame)
        if event == twilio.START:
            stream_sid, parameters = twilio.decode_start(frame)
            session.stream_sid = stream_sid
            session.call_sid = parameters.get("callSid")
            session.from_number = parameters.get("from")
            session.to_number = parameters.get("to")
            logger.info(
                "Call started: stream=%s call=%s from=%s",
                stream_sid,
                session.call_sid,
                session.from_number,
            )
            return parameters
        if event == twilio.STOP:
            return None
    return None


async def _twilio_to_agent(
    twilio_ws: WebSocket,
    agent: AsyncV1SocketClient,
    hangup: _Hangup,
) -> None:
    """Caller audio: Twilio -> Deepgram. Returns when the call is over."""
    async for raw in twilio_ws.iter_text():
        frame = twilio.decode_frame(raw)
        event = twilio.frame_event(frame)

        if event == twilio.MEDIA:
            await agent.send_media(twilio.decode_media_payload(frame))
        elif event == twilio.MARK:
            if twilio.decode_mark_name(frame) == f"{HANGUP_MARK}-{hangup.audio_chunks}":
                logger.debug("The goodbye has played; hanging up")
                return
        elif event == twilio.DTMF:
            logger.info("DTMF digit %s", twilio.decode_dtmf_digit(frame))
        elif event in (twilio.CONNECTED, twilio.START):
            pass
        elif event == twilio.STOP:
            break
        else:
            logger.warning("Unhandled Twilio event %r", event)


async def _agent_to_twilio(
    twilio_ws: WebSocket,
    agent: AsyncV1SocketClient,
    session: CallSession,
    hangup: _Hangup,
) -> None:
    """Agent audio and transcript: Deepgram -> Twilio."""
    loop = asyncio.get_running_loop()
    audio_bytes = 0
    async for message in agent:
        if isinstance(message, bytes):
            if session.stream_sid is None:
                continue
            for chunk in twilio.chunk_audio(message):
                await twilio_ws.send_text(twilio.media_frame(session.stream_sid, chunk))
            hangup.audio_chunks += 1
            hangup.last_audio_at = loop.time()
            audio_bytes += len(message)
            continue

        message_type = getattr(message, "type", None)
        if message_type not in _QUIET_EVENTS:
            if audio_bytes:
                logger.debug("Deepgram sent %.1f s of audio", audio_bytes / 8000)
                audio_bytes = 0
            logger.debug("Deepgram %s %s", message_type, getattr(message, "content", "") or "")

        if message_type == "ConversationText":
            session.transcript.append((message.role, message.content))
            if message.role == "assistant" and "goodbye" in message.content.lower() and hangup.goodbye_at is None:
                logger.info("Agent said goodbye on call %s", session.call_sid)
                hangup.goodbye_at = loop.time()
                hangup.timer = asyncio.create_task(_hang_up_after_goodbye(twilio_ws, session, hangup))
        elif message_type == "UserStartedSpeaking":
            # Twilio buffers everything we send it, so barge-in only works if
            # we drop that buffer the moment the caller starts talking.
            if session.stream_sid is not None:
                await twilio_ws.send_text(twilio.clear_frame(session.stream_sid))
        elif message_type == "AgentAudioDone":
            if session.stream_sid is not None:
                await twilio_ws.send_text(twilio.mark_frame(session.stream_sid, "agent-audio-done"))
        elif message_type == "Error":
            logger.error("Deepgram agent error %s: %s", message.code, message.description)
            break
        elif message_type == "Warning":
            logger.warning("Deepgram agent warning: %s", getattr(message, "description", message))


async def _hang_up_after_goodbye(twilio_ws: WebSocket, session: CallSession, hangup: _Hangup) -> None:
    """Once the goodbye's audio has all been sent, ask Twilio to say when it has played.

    A new mark goes out whenever more audio has been sent since the last one, so a
    mark that turned stale (audio sent after it) is replaced rather than trusted.
    """
    loop = asyncio.get_running_loop()
    marked_at = None
    while loop.time() - hangup.goodbye_at < HANGUP_TIMEOUT_SECONDS:
        await asyncio.sleep(HANGUP_POLL_SECONDS)
        now = loop.time()
        goodbye_audio_sent = hangup.last_audio_at > hangup.goodbye_at or now - hangup.goodbye_at >= CLOSING_AUDIO_WAIT_SECONDS
        quiet = now - hangup.last_audio_at >= AUDIO_QUIET_SECONDS
        if goodbye_audio_sent and quiet and marked_at != hangup.audio_chunks and session.stream_sid is not None:
            marked_at = hangup.audio_chunks
            await twilio_ws.send_text(twilio.mark_frame(session.stream_sid, f"{HANGUP_MARK}-{marked_at}"))
    logger.warning("Twilio never confirmed the goodbye played on call %s; hanging up", session.call_sid)
    hangup.done.set()


async def _keepalive(agent: AsyncV1SocketClient) -> None:
    while True:
        await asyncio.sleep(KEEPALIVE_SECONDS)
        await agent.send_keep_alive()
