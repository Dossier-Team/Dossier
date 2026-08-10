from datetime import datetime
from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    email: str
    phone_numer: str
    state: str
    on_dnc_since: datetime | None


class Company(BaseModel):
    id: int
    name: str
    known_aliases: list[str]
    address: str
    created_at: datetime
    num_distinct_users_violated: int
    violation_ids: list[int] = []


class Call(BaseModel):
    caller_company_id: int
    callee: User
    date: datetime
    from_number: str
    recording_url: str | None
    transcript: str | None
    is_solicitation: bool
    claimed_prior_relationship: bool
    callee_requested_stop: bool = False


class Violation(BaseModel):
    id: int
    callee_on_dnc: bool
    dnc_registered_at: datetime | None
    registration_lead_time_satisfied: bool

    callee: User

    first_call: Call
    second_call: Call
    additional_calls: list[Call] = []

    caller_company_id: int

    established_relationship_exception_applies: bool = False
    prior_express_consent_exception_applies: bool = False

    willful: bool = False

    flagged_at: datetime
    notes: str | None = None