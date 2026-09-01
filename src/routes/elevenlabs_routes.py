from elevenlabs.errors import BadRequestError
from fastapi import Request, Response, APIRouter, BackgroundTasks

from schemas.extraction import CallExtraction
from src.clients import elevenlabs, ELEVENLABS_WEBHOOK_SECRET, LLM_MODEL
from src.schemas.webhooks import ElevenLabsWebhookPayload

router = APIRouter()

@router.post("/elevenlabs/call-complete")
async def receive_post_call_webhook(request: Request, background_tasks: BackgroundTasks) -> Response:
    """
    Receives post call data from the ElevenLabs agent
    NOTE: must return a Response with status code 200 if successful otherwise it will be disabled by ElevenLabs
    """

    body = await request.body()
    signature = request.headers.get("elevenlabs-signature")

    try:
        event = elevenlabs.webhooks.construct_event(
            rawBody=body.decode("utf-8"),
            sig_header=signature,
            secret=ELEVENLABS_WEBHOOK_SECRET,
        )
    except BadRequestError:
        return Response(status_code=404)

    if event.get("type") == "post_call_transcription":
        payload = ElevenLabsWebhookPayload.model_validate(event)
        background_tasks.add_task(run_extraction_on_post_call_transcript, payload)

    # TODO: handle call initiation failure and audio event here

    return Response(status_code=200)

async def run_extraction_on_post_call_transcript(payload: ElevenLabsWebhookPayload) -> CallExtraction:
    transcript_text = payload.data.transcript

    structured_llm = LLM_MODEL.with_structured_output(CallExtraction)

    extraction =  await structured_llm.ainvoke(
        [
            (
                "system",
                "You are analyzing a transcript of a phone call between an AI agent "
                "posing as a potential scam victim and a suspected scammer. Extract "
                "every signal defined in the schema. Leave a field as None/[] when "
                "the transcript doesn't support it — never fabricate.",
            ),
            ("human", f"Transcript:\n\n{transcript_text}"),
        ]
    )

    print(extraction)
    return extraction