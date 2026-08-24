from elevenlabs.errors import BadRequestError
from fastapi import Request, Response, APIRouter, BackgroundTasks

from src.clients import elevenlabs, ELEVENLABS_WEBHOOK_SECRET
from src.schemas import ElevenLabsWebhookPayload
from src.tasks import run_extraction

router = APIRouter()

@router.post('/elevenlabs/call-complete')
async def receive_post_call_webhook(request: Request, background_tasks: BackgroundTasks) -> Response:
    """
    Receives post call data from the ElevenLabs agent
    NOTE: must return a Response with status code 200 if successful otherwise it will be disabled by ElevenLabs
    """

    body = await request.body()
    signature = request.headers.get('elevenlabs-signature')

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
        background_tasks.add_task(run_extraction, payload)

    # TODO: handle call initiation failure and audio event here

    return Response(status_code=200)
