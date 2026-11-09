"""After a call: pull out the details and send the call to getdossier.org.

getdossier.org does the rest — Jev classifies the problem, it's routed to a
team, logged, and a follow-up email is scheduled — and shows it on the Live page.
"""

import logging

from src.agent.prompts import COMPANY_NAME
from src.agent.session import CallSession
from src.clients import LLM_MODEL
from src.delivery.dossier import call_payload, send_to_dossier
from src.schemas.extraction import MaintenanceCall

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    f"You are reading the transcript of a call to {COMPANY_NAME}'s emergency maintenance line, "
    "between an automated agent and a tenant. Fill in each field from what the caller said. "
    "Leave a field empty when the transcript doesn't say it — never guess."
)


async def run_extraction_on_transcript(transcript_text: str) -> MaintenanceCall:
    structured_llm = LLM_MODEL.with_structured_output(MaintenanceCall)

    return await structured_llm.ainvoke(
        [
            ("system", SYSTEM_PROMPT),
            ("human", f"Transcript:\n\n{transcript_text}"),
        ]
    )


async def process_finished_call(session: CallSession) -> None:
    """Fired once the media socket closes. The transcript is sent even if extraction fails."""
    details = None
    try:
        details = await run_extraction_on_transcript(session.transcript_text)
        logger.info("Extraction for call %s: %s", session.call_sid, details.model_dump_json())
    except Exception:
        logger.exception("Couldn't extract details from call %s; sending the transcript alone", session.call_sid)

    if not await send_to_dossier(call_payload(session, details)):
        # The transcript exists nowhere else, so it goes in the log rather than being lost.
        logger.error("Couldn't send call %s to Dossier. Transcript:\n%s", session.call_sid, session.transcript_text)
