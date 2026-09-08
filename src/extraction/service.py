"""LLM extraction of structured intelligence from a finished call transcript.

Provider-agnostic on purpose: it takes transcript text, so it survived the move
off ElevenLabs' post-call webhook unchanged.
"""

import logging

from src.agent.session import CallSession
from src.clients import LLM_MODEL
from src.schemas.extraction import CallExtraction

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are analyzing a transcript of a phone call between an AI agent "
    "posing as a potential scam victim and a suspected scammer. Extract "
    "every signal defined in the schema. Leave a field as None/[] when "
    "the transcript doesn't support it — never fabricate."
)


async def run_extraction_on_transcript(transcript_text: str) -> CallExtraction:
    structured_llm = LLM_MODEL.with_structured_output(CallExtraction)

    return await structured_llm.ainvoke(
        [
            ("system", SYSTEM_PROMPT),
            ("human", f"Transcript:\n\n{transcript_text}"),
        ]
    )


async def extract_and_store(session: CallSession) -> CallExtraction:
    """Extract from a completed call. Fired once the media socket closes.

    TODO: persistence. Today this only logs the extraction — see the migration
    plan's open items for where these should land.
    """
    extraction = await run_extraction_on_transcript(session.transcript_text)
    logger.info(
        "Extraction for call %s from %s: %s",
        session.call_sid,
        session.from_number,
        extraction.model_dump_json(),
    )
    return extraction
