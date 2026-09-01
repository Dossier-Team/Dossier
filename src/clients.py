import os

from dotenv import load_dotenv
from elevenlabs import ElevenLabs
from langchain.chat_models import init_chat_model


load_dotenv()

elevenlabs = ElevenLabs(api_key=os.environ['ELEVENLABS_API_KEY'])
ELEVENLABS_WEBHOOK_SECRET = os.environ['ELEVENLABS_WEBHOOK_SECRET']
ELEVENLABS_AGENT_ID = os.environ['ELEVENLABS_AGENT_ID']

GEMINI_API_KEY = os.environ['GEMINI_API_KEY']
LLM_MODEL = init_chat_model("google_genai:gemini-3.7-flash")