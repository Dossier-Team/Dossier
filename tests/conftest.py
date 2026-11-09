import os

# src.clients reads these at import time. Tests never reach the real services.
for name, value in {
    "DEEPGRAM_API_KEY": "test-deepgram-key",
    "GEMINI_API_KEY": "test-gemini-key",
    "PUBLIC_HOST_NAME": "voice.example.org",
    "TWILIO_AUTH_TOKEN": "test-twilio-token",
    "CALL_INTAKE_TOKEN": "test-intake-token",
}.items():
    os.environ.setdefault(name, value)

import pytest


@pytest.fixture(autouse=True)
def no_call_status_posts(monkeypatch):
    """The bridge tells getdossier.org when a call starts. Tests must not."""
    import src.agent.bridge as bridge

    async def quiet(*_args, **_kwargs):
        return True

    monkeypatch.setattr(bridge, "send_call_status", quiet)
