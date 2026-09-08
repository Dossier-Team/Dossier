"""The audio bridge between a Twilio media socket and a Deepgram voice agent.

This is where the call actually happens: Twilio's mulaw frames go up to
Deepgram, Deepgram's synthesized audio comes back down, and the transcript
accumulates on the session as it goes. Deepgram has no post-call webhook — the
transcript exists only here, so whatever is on the session when this returns is
all the extraction step will ever see.
"""

import asyncio
import logging

from deepgram.agent.v1.socket_client import AsyncV1SocketClient
from fastapi import WebSocket

from src.agent.session import CallSession
from src.agent.settings import build_agent_settings
from src.clients import dg_client
from src.telephony import twilio_protocol as twilio

logger = logging.getLogger(__name__)

# Deepgram closes an idle agent socket. Scam calls have long silences — hold
# music, transfers — which is exactly the case that would trip it.
KEEPALIVE_SECONDS = 5.0


async def run_bridge(twilio_ws: WebSocket, session: CallSession) -> None:
    """Run the call to completion, filling in `session` as it goes.

    Returns when either side hangs up; raises whatever the losing task raised
    (`WebSocketDisconnect` on a normal caller hangup).
    """
    async with dg_client.agent.v1.connect() as agent:
        tasks = [
            asyncio.create_task(_twilio_to_agent(twilio_ws, agent, session)),
            asyncio.create_task(_agent_to_twilio(twilio_ws, agent, session)),
            asyncio.create_task(_keepalive(agent)),
        ]
        try:
            done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                task.result()
        finally:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)


async def _twilio_to_agent(
    twilio_ws: WebSocket,
    agent: AsyncV1SocketClient,
    session: CallSession,
) -> None:
    """Caller audio and call metadata: Twilio -> Deepgram."""
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
            await agent.send_settings(build_agent_settings(session))
        elif event == twilio.MEDIA:
            await agent.send_media(twilio.decode_media_payload(frame))
        elif event == twilio.DTMF:
            # Scammers push you through IVRs; worth seeing, nothing to do yet.
            logger.info("DTMF digit %s", twilio.decode_dtmf_digit(frame))
        elif event in (twilio.CONNECTED, twilio.MARK):
            pass
        elif event == twilio.STOP:
            break
        else:
            logger.warning("Unhandled Twilio event %r", event)


async def _agent_to_twilio(
    twilio_ws: WebSocket,
    agent: AsyncV1SocketClient,
    session: CallSession,
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
        elif message_type == "AgentAudioDone":
            if session.stream_sid is not None:
                await twilio_ws.send_text(
                    twilio.mark_frame(session.stream_sid, "agent-audio-done")
                )
        elif message_type == "Error":
            logger.error("Deepgram agent error %s: %s", message.code, message.description)
            break
        elif message_type == "Warning":
            logger.warning("Deepgram agent warning: %s", getattr(message, "description", message))


async def _keepalive(agent: AsyncV1SocketClient) -> None:
    while True:
        await asyncio.sleep(KEEPALIVE_SECONDS)
        await agent.send_keep_alive()
