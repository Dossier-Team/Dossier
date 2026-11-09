import os

from deepgram import AsyncDeepgramClient
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model


load_dotenv()


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f'{name} is not set. Add it to your .env (see .env.example) before starting the server.'
        )
    return value


GEMINI_API_KEY = _required_env('GEMINI_API_KEY')
LLM_MODEL = init_chat_model('google_genai:gemini-3.7-flash')

DEEPGRAM_API_KEY = _required_env('DEEPGRAM_API_KEY')
dg_client = AsyncDeepgramClient(api_key=DEEPGRAM_API_KEY)

PUBLIC_HOST_NAME = _required_env('PUBLIC_HOST_NAME')

# Checks that requests come from Twilio, and signs each call's media stream.
TWILIO_AUTH_TOKEN = _required_env('TWILIO_AUTH_TOKEN')

# Where finished calls go. The same token is set on the getdossier.org Worker.
CALL_INTAKE_URL = os.environ.get('CALL_INTAKE_URL') or 'https://getdossier.org/demo/api/inbound/call'
CALL_INTAKE_TOKEN = _required_env('CALL_INTAKE_TOKEN')
