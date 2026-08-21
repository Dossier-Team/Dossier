import os

from dotenv import load_dotenv
from fastapi import Request, Response, APIRouter
from elevenlabs import ElevenLabs
from elevenlabs.errors import BadRequestError


router = APIRouter(prefix='/agent')

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
async def receive_post_call_transcription(request: Request) -> Response:
    pass