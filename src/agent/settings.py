from deepgram.agent.v1 import (
    AgentV1Settings,
    AgentV1SettingsAgent,
    AgentV1SettingsAgentListen,
    AgentV1SettingsAgentListenProvider_V2,
    AgentV1SettingsAudio,
    AgentV1SettingsAudioInput,
    AgentV1SettingsAudioOutput,
)
from deepgram.types import (
    ThinkSettingsV1,
    ThinkSettingsV1Provider_Google,
    SpeakSettingsV1,
    SpeakSettingsV1Provider_Deepgram,
)

from src.agent.prompts import GREETING, PROMPT
from src.agent.session import CallSession

TWILIO_ENCODING = "mulaw"
TWILIO_SAMPLE_RATE = 8000

STT_MODEL = "flux-general-en"
TTS_MODEL = "aura-2-thalia-en"
THINK_MODEL = "gemini-2.5-flash"

LISTEN_PROVIDER = AgentV1SettingsAgentListenProvider_V2(type="deepgram", model=STT_MODEL)
SPEAK_PROVIDER = SpeakSettingsV1Provider_Deepgram(type="deepgram", model=TTS_MODEL)
THINK_PROVIDER = ThinkSettingsV1Provider_Google(type="google", model=THINK_MODEL)


def build_agent_settings(session: CallSession) -> AgentV1Settings:
    """The `Settings` message sent once, right after Twilio's `start` frame."""
    return AgentV1Settings(
        type="Settings",
        audio=AgentV1SettingsAudio(
            input=AgentV1SettingsAudioInput(
                encoding=TWILIO_ENCODING,
                sample_rate=TWILIO_SAMPLE_RATE,
            ),
            output=AgentV1SettingsAudioOutput(
                encoding=TWILIO_ENCODING,
                sample_rate=TWILIO_SAMPLE_RATE,
                container="none",
            ),
        ),
        agent=AgentV1SettingsAgent(
            listen=AgentV1SettingsAgentListen(provider=LISTEN_PROVIDER),
            think=ThinkSettingsV1(provider=THINK_PROVIDER, prompt=PROMPT),
            speak=SpeakSettingsV1(provider=SPEAK_PROVIDER),
            greeting=GREETING,
        ),
    )
