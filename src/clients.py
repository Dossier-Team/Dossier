import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model


load_dotenv()

GEMINI_API_KEY = os.environ['GEMINI_API_KEY']
PUBLIC_HOST_NAME = os.environ['PUBLIC_HOST_NAME']
LLM_MODEL = init_chat_model('google_genai:gemini-3.7-flash')