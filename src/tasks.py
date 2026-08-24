from src.extraction import extract_call_info
from src.schemas import ElevenLabsWebhookPayload


def run_extraction(payload: ElevenLabsWebhookPayload) -> None:
    """Background task: extract structured intel from a completed call's transcript.

    Kept separate from the webhook route so persistence (or anything else) can
    be added here later without touching the route or the extraction chain.
    """

    result = extract_call_info(payload.data.transcript)
    print(result)
