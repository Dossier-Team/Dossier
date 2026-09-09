from datetime import datetime, timezone
from pydantic import BaseModel, Field


class CallSession(BaseModel):
    """Per-call state shared by the bridge, the route, and the extraction step.

    Everything here is populated as the call progresses: the Twilio `start`
    frame fills in the stream sid and the metadata passed through as
    `<Parameter>`s, and the Deepgram `ConversationText` events fill in the
    transcript.
    """

    stream_sid: str | None = None
    call_sid: str | None = None
    from_number: str | None = None
    to_number: str | None = None
    transcript: list[tuple[str, str]] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def transcript_text(self) -> str:
        """The transcript as `role: content` lines, ready for the extraction prompt."""
        return "\n".join(f"{role}: {content}" for role, content in self.transcript)
