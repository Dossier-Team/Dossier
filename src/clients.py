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
llm_model = init_chat_model('google_genai:gemini-3.7-flash')

DEEPGRAM_API_KEY = _required_env('DEEPGRAM_API_KEY')
dg_client = AsyncDeepgramClient(api_key=DEEPGRAM_API_KEY)

PUBLIC_HOST_NAME = _required_env('PUBLIC_HOST_NAME')
