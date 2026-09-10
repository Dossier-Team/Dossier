import os

from deepgram import AsyncDeepgramClient
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


load_dotenv()


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f'{name} is not set. Add it to your .env (see .env.example) before starting the server.'
        )
    return value


# Read by init_chat_model from the environment, so it is only validated here.
GEMINI_API_KEY = _required_env('GEMINI_API_KEY')
# Shared LangChain chat model used for every LLM call in the app.
llm_model = init_chat_model('google_genai:gemini-3.7-flash')

DEEPGRAM_API_KEY = _required_env('DEEPGRAM_API_KEY')
# Async Deepgram SDK client to create voice agent.
deepgram_client = AsyncDeepgramClient(api_key=DEEPGRAM_API_KEY)

# Publicly reachable host for this server, used to build callback/webhook URLs.
PUBLIC_HOST_NAME = _required_env('PUBLIC_HOST_NAME')

DATABASE_URL = _required_env('DATABASE_URL')
# Async SQLAlchemy engine holding the connection pool for the whole process.
engine = create_async_engine(DATABASE_URL)

# Factory for AsyncSession objects bound to the engine above.
# expire_on_commit=False keeps ORM instances usable after a commit, so
# response models can still read their attributes without another query.
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session():
    """Yield a request-scoped AsyncSession, closed when the request finishes."""
    async with async_session_maker() as session:
        yield session