from datetime import datetime

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel

from models import CallRecord, Callee, Caller

EXTRACTION_PROMPT = """Read the following phone call transcript and extract the caller's \
name, company (if mentioned), whether they claimed a prior relationship with the callee, \
whether the call was a solicitation, whether the callee asked to stop being contacted, and \
any other notable notes. Leave a field unset if the transcript doesn't make it clear.

Transcript:
{transcript}"""


class _ExtractedFields(BaseModel):
    caller_name: str | None = None
    caller_company_name: str | None = None
    claimed_prior_relationship: bool | None = None
    is_solicitation: bool | None = None
    requested_stop: bool = False
    notes: str | None = None


def extract_call_record(
    model: BaseChatModel,
    transcript: str,
    call_date: datetime,
    caller_phone: str,
    callee_phone: str,
) -> CallRecord:
    structured_model = model.with_structured_output(_ExtractedFields)
    extracted: _ExtractedFields = structured_model.invoke(
        EXTRACTION_PROMPT.format(transcript=transcript)
    )

    return CallRecord(
        call_date=call_date,
        transcript=transcript,
        caller=Caller(
            name=extracted.caller_name,
            phone_number=caller_phone,
            company_name=extracted.caller_company_name,
            claimed_prior_relationship=extracted.claimed_prior_relationship,
        ),
        callee=Callee(phone_number=callee_phone),
        is_solicitation=extracted.is_solicitation,
        requested_stop=extracted.requested_stop,
        notes=extracted.notes,
    )
