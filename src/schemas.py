from pydantic import BaseModel


class ElevenLabsWebhookData(BaseModel):
    agent_id: str
    conversation_id: str
    transcript: list
    metadata: None
    analysis: None


class ElevenLabsWebhookPayload(BaseModel):
    """Top-level fields of a ElevenLabs post-call webhook."""

    type: str
    data: ElevenLabsWebhookData
    event_timestamp: int | None