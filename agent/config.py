import os

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

DEFAULT_CONVERSATION_MODEL = "anthropic:claude-sonnet-4-5"
DEFAULT_EXTRACTION_MODEL = "anthropic:claude-haiku-4-5"


def get_conversation_model() -> BaseChatModel:
    model = os.environ.get("CONVERSATION_MODEL", DEFAULT_CONVERSATION_MODEL)
    return init_chat_model(model)


def get_extraction_model() -> BaseChatModel:
    model = os.environ.get("EXTRACTION_MODEL", DEFAULT_EXTRACTION_MODEL)
    return init_chat_model(model)
