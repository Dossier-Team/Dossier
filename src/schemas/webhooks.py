from pydantic import BaseModel


class AgentPostCallTranscript(BaseModel):
    agent_id: str
    conversation_id: str
    transcript: list
    # metadata: None
    # analysis: None


class ElevenLabsWebhookPayload(BaseModel):
    """Top-level fields of a ElevenLabs post-call webhook."""

    type: str
    data: AgentPostCallTranscript
    event_timestamp: int | None
