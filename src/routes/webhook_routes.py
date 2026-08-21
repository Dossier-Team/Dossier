from fastapi import Request, Response, APIRouter
from elevenlabs.errors import BadRequestError

from src.clients import ELEVENLABS_AGENT_ID, elevenlabs, ELEVENLABS_WEBHOOK_SECRET
from src.schemas import ElevenLabsWebhookPayload

router = APIRouter(prefix='/routes')


@router.post('/twilio/inbound')
async def handle_inbound_call(request: Request) -> Response:
    form = await request.form()
    from_number = form.get('From')
    to_number = form.get('To')

    twiml = elevenlabs.conversational_ai.twilio.register_call(
        agent_id=ELEVENLABS_AGENT_ID,
        from_number=from_number,
        to_number=to_number,
        direction='inbound',
    )

    return Response(content=twiml, media_type='application/xml')


@router.post('/elevenlabs/call-complete')
async def receive_post_call_webhook(request: Request) -> Response:
    payload = await request.body()
    signature = request.headers.get('elevenlabs-signature')

    try:
        event = elevenlabs.webhooks.construct_event(
            rawBody=payload.decode("utf-8"),
            sig_header=signature,
            secret=ELEVENLABS_WEBHOOK_SECRET,
        )
    except BadRequestError:
        return Response(status_code=404)

    if event.get("type") == "post_call_transcription":
        payload = ElevenLabsWebhookPayload.model_validate(event)
        print(payload.data.transcript)

    return Response(status_code=200)
