import os

from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel

load_dotenv()

_PROVIDERS = {
    'anthropic': ('langchain_anthropic', 'ChatAnthropic'),
    'openai': ('langchain_openai', 'ChatOpenAI'),
    'gemini': ('langchain_google_genai', 'ChatGoogleGenerativeAI'),
}


def get_llm() -> BaseChatModel:
    """Return a LangChain chat model chosen via LLM_PROVIDER/LLM_MODEL env vars.

    Callers should depend only on the returned BaseChatModel interface so the
    provider can be swapped by changing env vars alone.
    """

    provider = os.environ.get('LLM_PROVIDER', 'anthropic').lower()
    model = os.environ.get('LLM_MODEL')

    if provider not in _PROVIDERS:
        raise ValueError(f'Unsupported LLM_PROVIDER: {provider!r}. Expected one of {list(_PROVIDERS)}.')

    module_name, class_name = _PROVIDERS[provider]
    module = __import__(module_name, fromlist=[class_name])
    chat_model_cls = getattr(module, class_name)

    kwargs = {"model": model} if model else {}
    return chat_model_cls(**kwargs)
