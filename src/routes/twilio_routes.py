import asyncio
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Request, Response, WebSocket, WebSocketDisconnect

from src.agent.bridge import StreamRejected, announce_call, run_bridge
from src.agent.session import CallSession
from src.clients import PUBLIC_HOST_NAME, TWILIO_AUTH_TOKEN
from src.extraction.service import process_finished_call
from src.telephony.security import is_from_twilio, stream_token
from src.telephony.twiml import build_stream_twiml

logger = logging.getLogger(__name__)

router = APIRouter()

# Extraction outlives the request that started it, so hold a reference —
# asyncio only keeps a weak one and would let the task be collected mid-flight.
_extraction_tasks: set[asyncio.Task] = set()


def _public_url(request: Request) -> str:
    """The URL Twilio called and signed. Behind the proxy the app sees http://localhost instead."""
    query = f"?{request.url.query}" if request.url.query else ""
    return f"https://{PUBLIC_HOST_NAME}{request.url.path}{query}"


@router.post("/twiml")
async def twiml(request: Request) -> Response:
    form = await request.form()
    params = {name: str(value) for name, value in form.items()}
    if not is_from_twilio(TWILIO_AUTH_TOKEN, _public_url(request), params, request.headers.get("x-twilio-signature")):
        logger.warning("Rejected an inbound-call webhook with a bad signature")
        return Response(status_code=403)

    call_sid = params.get("CallSid")
    if not call_sid:
        return Response(status_code=400)
    xml = build_stream_twiml(
        host=PUBLIC_HOST_NAME,
        call_sid=call_sid,
        from_number=params.get("From"),
        to_number=params.get("To"),
        token=stream_token(TWILIO_AUTH_TOKEN, call_sid),
    )
    return Response(content=xml, media_type="application/xml")


@router.websocket("/media")
async def media(twilio_ws: WebSocket) -> None:
    await twilio_ws.accept()
    session = CallSession()
    rejected = False
    try:
        await run_bridge(twilio_ws, session)
        # The agent hung up, or the stream ended. Closing ends <Connect>, and the call with it.
        await _close(twilio_ws)
    except StreamRejected as error:
        rejected = True
        logger.warning("%s", error)
        await _close(twilio_ws, code=1008)
    except WebSocketDisconnect:
        pass
    finally:
        session.ended_at = datetime.now(timezone.utc)
        if session.transcript:
            task = asyncio.create_task(process_finished_call(session))
            _extraction_tasks.add(task)
            task.add_done_callback(_extraction_tasks.discard)
        else:
            logger.info("Call %s ended with an empty transcript", session.call_sid)
            # A call with a transcript is marked over when it's posted. One without needs saying.
            if session.call_sid and not rejected:
                announce_call(session, "ended")


async def _close(twilio_ws: WebSocket, code: int = 1000) -> None:
    try:
        await twilio_ws.close(code=code)
    except RuntimeError:
        pass  # Twilio already closed it.
