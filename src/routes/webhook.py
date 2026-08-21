import os

from dotenv import load_dotenv
from fastapi import Request, Response, APIRouter
from elevenlabs import ElevenLabs
from elevenlabs.errors import BadRequestError


router = APIRouter(prefix='/agent')

load_dotenv()
elevenlabs = ElevenLabs(api_key=os.environ['ELEVENLABS_API_KEY'])
WEBHOOK_SECRET = os.environ['ELEVENLABS_WEBHOOK_SECRET']


@router.post('/elevenlabs/call-complete')
async def handle_call_complete(request: Request) -> Response:
    return Response(status_code=200)