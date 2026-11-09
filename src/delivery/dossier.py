"""Sending a finished call to getdossier.org."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

import httpx

from src.agent.session import SPEAKERS, CallSession
from src.clients import CALL_INTAKE_TOKEN, CALL_INTAKE_URL
from src.schemas.extraction import MaintenanceCall

logger = logging.getLogger(__name__)

# Waits between attempts. A 4xx isn't retried: sending the same thing again won't fix it.
RETRY_DELAYS_SECONDS = (2.0, 5.0)
TIMEOUT_SECONDS = 20.0
STATUS_TIMEOUT_SECONDS = 5.0


def call_payload(session: CallSession, details: MaintenanceCall | None) -> dict[str, Any]:
    return {
        "call_sid": session.call_sid,
        "from_number": session.from_number,
        "to_number": session.to_number,
        "started_at": session.started_at.isoformat(),
        "ended_at": (session.ended_at or datetime.now(timezone.utc)).isoformat(),
        "transcript": [{"speaker": SPEAKERS.get(role, role), "text": text} for role, text in session.transcript],
        "details": details.model_dump() if details else None,
    }


async def send_to_dossier(
    payload: dict[str, Any],
    *,
    url: str = CALL_INTAKE_URL,
    token: str = CALL_INTAKE_TOKEN,
    delays: tuple[float, ...] = RETRY_DELAYS_SECONDS,
    transport: httpx.AsyncBaseTransport | None = None,
) -> bool:
    """POST the call to getdossier.org. Returns whether it was accepted."""
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS, transport=transport) as client:
        for attempt in range(len(delays) + 1):
            if attempt:
                await asyncio.sleep(delays[attempt - 1])
            try:
                response = await client.post(url, json=payload, headers=headers)
            except httpx.TransportError as error:
                logger.warning("Sending call %s to Dossier failed: %s", payload.get("call_sid"), error)
                continue
            if response.is_success:
                logger.info("Call %s logged on Dossier: %s", payload.get("call_sid"), response.text)
                return True
            logger.warning(
                "Dossier answered %s for call %s: %s", response.status_code, payload.get("call_sid"), response.text
            )
            if response.status_code < 500:
                return False
    return False


async def send_call_status(
    call_sid: str | None,
    from_number: str | None,
    status: str,
    *,
    url: str = CALL_INTAKE_URL,
    token: str = CALL_INTAKE_TOKEN,
    transport: httpx.AsyncBaseTransport | None = None,
) -> bool:
    """Tell getdossier.org a call has started, or ended with nothing said, so the Live page can show
    "On a call". One try and a short timeout: it only drives the page, and a miss must not hold up the call."""
    if not call_sid:
        return False
    try:
        async with httpx.AsyncClient(timeout=STATUS_TIMEOUT_SECONDS, transport=transport) as client:
            response = await client.post(
                f"{url.rstrip('/')}/status",
                json={"call_sid": call_sid, "from_number": from_number, "status": status},
                headers={"Authorization": f"Bearer {token}"},
            )
    except httpx.HTTPError as error:
        logger.warning("Couldn't tell Dossier call %s %s: %s", call_sid, status, error)
        return False
    if not response.is_success:
        logger.warning("Dossier answered %s to call %s %s: %s", response.status_code, call_sid, status, response.text)
    return response.is_success
