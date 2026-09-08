from fastapi import APIRouter, Request, Response
from src.clients import elevenlabs, ELEVENLABS_AGENT_ID

router = APIRouter()

@router.post("/twiml")
async def twiml(request: Request) -> Response:
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Connect>
    <Stream url="wss://{PUBLIC_HOSTNAME}/media" />
  </Connect>
</Response>"""
    return Response(content=xml, media_type="application/xml")


# @router.post('/twilio/inbound')
# async def handle_inbound_call(request: Request) -> Response:
#     """
#     Opens a bidirectional WebSocket allowing agent to receive call audio
#     and for agent's response to be received back
#     """
#
#     form = await request.form()
#     from_number = form.get('From')
#     to_number = form.get('To')
#
#     twiml = elevenlabs.conversational_ai.twilio.register_call(
#         agent_id=ELEVENLABS_AGENT_ID,
#         from_number=from_number,
#         to_number=to_number,
#         direction='inbound',
#     )
#
#     return Response(content=twiml, media_type='application/xml')