import os

from dotenv import load_dotenv
from elevenlabs import ElevenLabs

load_dotenv()

elevenlabs = ElevenLabs(api_key=os.environ['ELEVENLABS_API_KEY'])
ELEVENLABS_WEBHOOK_SECRET = os.environ['ELEVENLABS_WEBHOOK_SECRET']
ELEVENLABS_AGENT_ID = os.environ['ELEVENLABS_AGENT_ID']