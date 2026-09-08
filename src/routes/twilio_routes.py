import asyncio
import logging

from fastapi import APIRouter, Request, Response, WebSocket, WebSocketDisconnect

from src.agent.bridge import run_bridge
from src.agent.session import CallSession
from src.clients import PUBLIC_HOST_NAME
from src.extraction.service import extract_and_store
from src.telephony.twiml import build_stream_twiml

logger = logging.getLogger(__name__)

router = APIRouter()

# Extraction outlives the request that started it, so hold a reference —
# asyncio only keeps a weak one and would let the task be collected mid-flight.
_extraction_tasks: set[asyncio.Task] = set()


@router.post("/twiml")
async def twiml(request: Request) -> Response:
    form = await request.form()
    xml = build_stream_twiml(
        host=PUBLIC_HOST_NAME,
        call_sid=form.get("CallSid"),
        from_number=form.get("From"),
        to_number=form.get("To"),
    )
    return Response(content=xml, media_type="application/xml")


@router.websocket("/media")
async def media(twilio_ws: WebSocket) -> None:
    await twilio_ws.accept()
    session = CallSession()
    try:
        await run_bridge(twilio_ws, session)
    except WebSocketDisconnect:
        pass
    finally:
        if session.transcript:
            task = asyncio.create_task(extract_and_store(session))
            _extraction_tasks.add(task)
            task.add_done_callback(_extraction_tasks.discard)
        else:
            logger.info("Call %s ended with an empty transcript", session.call_sid)
