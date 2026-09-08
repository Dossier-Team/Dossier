"""Deepgram Voice Agent configuration.

Built with the SDK's typed constructors rather than `model_validate` on a raw
dict, so a schema mistake surfaces here at import instead of on the first call.
"""

from deepgram.agent.v1 import (
    AgentV1Settings,
    AgentV1SettingsAgent,
    AgentV1SettingsAgentListen,
    AgentV1SettingsAgentListenProvider_V2,
    AgentV1SettingsAgentSpeakEndpoint,
    AgentV1SettingsAgentSpeakEndpointProvider_Deepgram,
    AgentV1SettingsAudio,
    AgentV1SettingsAudioInput,
    AgentV1SettingsAudioOutput,
)
from deepgram.types import ThinkSettingsV1

from src.agent.prompts import GREETING, PROMPT
from src.agent.session import CallSession

# Twilio Media Streams speak and listen mulaw at 8 kHz in both directions;
# anything else here means resampling in the bridge.
TWILIO_ENCODING = "mulaw"
TWILIO_SAMPLE_RATE = 8000

STT_MODEL = "flux-general-en"
# Flux (speak v2) is not in the SDK's voice list and is unconfirmed for
# mulaw/8000; Aura 2 on v1 definitely supports it. See the migration plan's
# open items before switching this to a flux-* voice.
TTS_MODEL = "aura-2-thalia-en"
TTS_VERSION = "v1"
# No API key is sent for the LLM, so Deepgram bills its managed model. This is
# a third LLM in the stack, separate from LLM_MODEL used for extraction.
THINK_PROVIDER = {"type": "open_ai", "model": "gpt-4o-mini"}


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
            listen=AgentV1SettingsAgentListen(
                provider=AgentV1SettingsAgentListenProvider_V2(
                    type="deepgram",
                    model=STT_MODEL,
                ),
            ),
            think=ThinkSettingsV1(provider=THINK_PROVIDER, prompt=PROMPT),
            speak=AgentV1SettingsAgentSpeakEndpoint(
                provider=AgentV1SettingsAgentSpeakEndpointProvider_Deepgram(
                    version=TTS_VERSION,
                    model=TTS_MODEL,
                ),
            ),
            greeting=GREETING,
        ),
    )
