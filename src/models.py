from datetime import datetime
from pydantic import BaseModel


class Caller(BaseModel):
    name: str | None = None
    phone_number: str
    company_name: str | None = None
    claimed_prior_relationship: bool | None = None


class Callee(BaseModel):
    name: str | None = None
    phone_number: str
    state: str | None = None


class CallRecord(BaseModel):
    call_date: datetime
    recording_url: str | None = None
    transcript: str | None = None

    caller: Caller
    callee: Callee

    is_solicitation: bool | None = None
    requested_stop: bool = False
    notes: str | None = None