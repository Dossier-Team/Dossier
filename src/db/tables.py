from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Column, JSON


class Call(SQLModel, table=True):
    __tablename__ = "calls"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    from_number: str | None = None
    to_number: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None


class Transcript(SQLModel, table=True):
    __tablename__ = "transcripts"

    call_id: UUID = Field(foreign_key="calls.id", unique=True, index=True)
    raw_transcript: list = Field(sa_column=Column(JSON))


# class BrandClaimed(SQLModel, table=True):
#     __tablename__ = "brands_claimed"
#
#     id: UUID = Field(default_factory=uuid4, primary_key=True) # TODO: Do we really need a unique id for each row
#     call_id: UUID = Field(foreign_key="calls.id", unique=True, index=True)
#     name: str | None
#     position: str | None
#     department: str | None
#     created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
#
#
# class Scammer(SQLModel, table=True):
#     __tablename__ = "scammers"
#
#     name: str | None
#     location: str | None
#     script_summary: str | None
#     remote_access_tools_used: list[str] | None
#
#
# class PaymentMethod(SQLModel, table=True):
#     __tablename__ = "payment_methods"
#
#     id: UUID = Field(default_factory=uuid4, primary_key=True)
#     call_id: UUID = Field(foreign_key="calls.id", unique=True, index=True)
#     name: str | None
#     operator: str | None
#     amount: float | None
#
#
# class CallbackNumber(SQLModel, table=True):
#     __tablename__ = "callback_numbers"
#
#     id: UUID = Field(default_factory=uuid4, primary_key=True)
#     call_id: UUID = Field(foreign_key="calls.id", index=True)
#     phone_number: str
#     order_mentioned: int | None = None
#
#
# class PersonalDataExposure(SQLModel, table=True):
#     __tablename__ = "personal_data_exposures"
#
#     id: UUID = Field(default_factory=uuid4, primary_key=True)
#     call_id: UUID = Field(foreign_key="calls.id", index=True)
#     data_point: str