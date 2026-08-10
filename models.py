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
    name: str
    known_aliases: list[str]
    address: str
    created_at: datetime
    num_distinct_users_violated: int
    violations: list['Violation']


class Call(BaseModel):
    caller: Company
    callee: User
    date: datetime
    from_number: str                    # calling number as received (may be spoofed)
    recording_url: str | None
    transcript: str | None
    is_solicitation: bool               # extracted: was this a telephone solicitation
    claimed_prior_relationship: bool    # did caller assert an established business relationship
    callee_requested_stop: bool = False # did callee explicitly ask to stop calling (willfulness signal)


class Violation(BaseModel):
    # 1. Registry status
    callee_on_dnc: bool
    dnc_registered_at: datetime | None       # from callee.on_dnc_since
    registration_lead_time_satisfied: bool   # >=31 days before first_call.date

    # 2. Identity of the number's owner/user
    callee: User

    # 3. Calls (>=2 within rolling 12-month window)
    first_call: Call
    second_call: Call
    additional_calls: list[Call] = []

    # 4. Identity of calling entity
    caller: Company

    # 5. Absence of exceptions
    established_relationship_exception_applies: bool = False
    prior_express_consent_exception_applies: bool = False

    # 6. Willfulness (for treble damages, not base claim)
    willful: bool = False   # e.g. True if any call has callee_requested_stop=True and a later call still occurred

    # Meta
    flagged_at: datetime
    notes: str | None = None