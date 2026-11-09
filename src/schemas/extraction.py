from pydantic import BaseModel, Field


class MaintenanceCall(BaseModel):
    """What the maintenance team needs from a call to the emergency line.

    Leave fields as None when the caller didn't say — do not fabricate.
    """

    caller_name: str | None = Field(default=None, description="The caller's name.")
    address: str | None = Field(
        default=None,
        description="Street address and unit number, with numbers as digits (e.g. '118 Catherine Street, unit 2B').",
    )
    callback_number: str | None = Field(
        default=None,
        description="A number to call back on, only if the caller gave one other than the number they called from.",
    )
    problem: str | None = Field(
        default=None,
        description="What's wrong, in one to three sentences close to the caller's own words:"
                    " what is broken, where in the unit, since when, how bad. No diagnosis or advice.",
    )
    email: str | None = Field(
        default=None,
        description="The caller's email address written normally (e.g. jordan.lee@gmail.com),"
                    " as it was last read back to them.",
    )
    email_confirmed: bool = Field(
        default=False,
        description="True only if the agent read the email back and the caller said it was right.",
    )
