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

from deepgram.agent.v1 import AgentV1SendFunctionCallResponse
from deepgram.agent.v1.socket_client import AsyncV1SocketClient
from fastapi import WebSocket

from src.agent.prompts import END_CALL
from src.agent.session import CallSession
from src.agent.settings import build_agent_settings
from src.clients import TWILIO_AUTH_TOKEN, dg_client
from src.telephony import twilio_protocol as twilio
from src.telephony.security import is_valid_stream_token

logger = logging.getLogger(__name__)

# Deepgram closes an idle agent socket, so it gets a keepalive through long silences.
KEEPALIVE_SECONDS = 5.0

# The goodbye's audio can start arriving just after the end_call request, so wait this long for it.
HANGUP_GRACE_SECONDS = 1.5
# If Twilio never confirms the goodbye has played, hang up anyway.
HANGUP_TIMEOUT_SECONDS = 20.0
HANGUP_MARK = "hangup"


class StreamRejected(Exception):
    """The media stream didn't carry a token from our inbound-call webhook."""


@dataclass
class _Hangup:
    """Hanging up once the goodbye has finished playing, not while it's still being said."""

    requested: bool = False
    agent_speaking: bool = False
    done: asyncio.Event = field(default_factory=asyncio.Event)
    timer: asyncio.Task | None = None


async def run_bridge(twilio_ws: WebSocket, session: CallSession) -> None:
    """Run the call to completion, filling in `session` as it goes.

    Returns when either side hangs up or the agent ends the call; raises
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
            # Twilio echoes a mark once everything queued before it has played.
            if twilio.decode_mark_name(frame) == HANGUP_MARK and hangup.requested and not hangup.agent_speaking:
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
    async for message in agent:
        if isinstance(message, bytes):
            if session.stream_sid is None:
                continue
            for chunk in twilio.chunk_audio(message):
                await twilio_ws.send_text(twilio.media_frame(session.stream_sid, chunk))
            continue

        message_type = getattr(message, "type", None)
        if message_type == "ConversationText":
            session.transcript.append((message.role, message.content))
        elif message_type == "UserStartedSpeaking":
            # Twilio buffers everything we send it, so barge-in only works if
            # we drop that buffer the moment the caller starts talking.
            if session.stream_sid is not None:
                await twilio_ws.send_text(twilio.clear_frame(session.stream_sid))
        elif message_type == "AgentStartedSpeaking":
            hangup.agent_speaking = True
        elif message_type == "AgentAudioDone":
            hangup.agent_speaking = False
            if session.stream_sid is not None:
                name = HANGUP_MARK if hangup.requested else "agent-audio-done"
                await twilio_ws.send_text(twilio.mark_frame(session.stream_sid, name))
        elif message_type == "FunctionCallRequest":
            for function in message.functions:
                await _answer_function_call(twilio_ws, agent, session, hangup, function)
        elif message_type == "Error":
            logger.error("Deepgram agent error %s: %s", message.code, message.description)
            break
        elif message_type == "Warning":
            logger.warning("Deepgram agent warning: %s", getattr(message, "description", message))


async def _answer_function_call(twilio_ws, agent, session: CallSession, hangup: _Hangup, function) -> None:
    if function.name == END_CALL:
        content = "Hanging up now."
        if not hangup.requested:
            logger.info("Agent ended call %s", session.call_sid)
            hangup.requested = True
            hangup.timer = asyncio.create_task(_hang_up_after_goodbye(twilio_ws, session, hangup))
    else:
        logger.warning("Agent called unknown function %r", function.name)
        content = f"There's no function called {function.name}."
    if function.client_side:
        await agent.send_function_call_response(
            AgentV1SendFunctionCallResponse(id=function.id, name=function.name, content=content)
        )


async def _hang_up_after_goodbye(twilio_ws: WebSocket, session: CallSession, hangup: _Hangup) -> None:
    """If the goodbye was already sent, ask Twilio to say when it has played. Otherwise
    `AgentAudioDone` sends that mark once the goodbye's audio is done."""
    await asyncio.sleep(HANGUP_GRACE_SECONDS)
    if not hangup.agent_speaking and session.stream_sid is not None:
        await twilio_ws.send_text(twilio.mark_frame(session.stream_sid, HANGUP_MARK))
    await asyncio.sleep(HANGUP_TIMEOUT_SECONDS)
    logger.warning("Twilio never confirmed the goodbye played on call %s; hanging up", session.call_sid)
    hangup.done.set()


async def _keepalive(agent: AsyncV1SocketClient) -> None:
    while True:
        await asyncio.sleep(KEEPALIVE_SECONDS)
        await agent.send_keep_alive()
