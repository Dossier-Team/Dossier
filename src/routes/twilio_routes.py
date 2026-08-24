from fastapi import APIRouter, Request, Response
from src.clients import elevenlabs, ELEVENLABS_AGENT_ID

router = APIRouter()

@router.post('/twilio/inbound')
async def handle_inbound_call(request: Request) -> Response:
    """
    When Twilio receives an inbound call passes the call to the ElevenLabs Agent
    """

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