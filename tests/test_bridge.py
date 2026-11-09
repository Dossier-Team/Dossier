"""The bridge, with a fake Twilio socket and a fake Deepgram agent."""

import asyncio
import json
from types import SimpleNamespace

import pytest

import src.agent.bridge as bridge
from src.agent.session import CallSession
from src.telephony.security import stream_token


class FakeTwilio:
    """Plays the caller's side. Echoes each mark `echo_delay` seconds after it's sent, as if the
    audio before it had just finished playing; never, if `echo_delay` is None."""

    def __init__(self, call_sid="CA1", token=None, echo_delay=0.0):
        self.inbound: asyncio.Queue = asyncio.Queue()
        self.sent: list[dict] = []
        self.echo_delay = echo_delay
        self.inbound.put_nowait({"event": "connected"})
        self.inbound.put_nowait({
            "event": "start",
            "start": {
                "streamSid": "MZ1",
                "customParameters": {"callSid": call_sid, "from": "+16075550199", "to": "+16075550100",
                                     "token": token or stream_token("test-twilio-token", call_sid)},
            },
        })

    async def iter_text(self):
        while True:
            frame = await self.inbound.get()
            if frame is None:
                return
            yield json.dumps(frame)

    async def send_text(self, text):
        frame = json.loads(text)
        self.sent.append(frame)
        if frame["event"] == "mark" and self.echo_delay is not None:
            echo = {"event": "mark", "streamSid": "MZ1", "mark": frame["mark"]}
            asyncio.get_running_loop().call_later(self.echo_delay, self.inbound.put_nowait, echo)

    def marks(self):
        return [frame["mark"]["name"] for frame in self.sent if frame["event"] == "mark"]


def text(role, content):
    return SimpleNamespace(type="ConversationText", role=role, content=content)


def message(kind):
    return SimpleNamespace(type=kind)


def pause(seconds):
    async def wait():
        await asyncio.sleep(seconds)
    return wait


class FakeAgent:
    """Says its script in order, then stays connected with nothing more to say."""

    def __init__(self, script):
        self.script = script
        self.settings = None
        self.media: list[bytes] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def send_settings(self, settings):
        self.settings = settings

    async def send_media(self, audio):
        self.media.append(audio)

    async def send_keep_alive(self):
        pass

    async def __aiter__(self):
        for item in self.script:
            await asyncio.sleep(0)
            if callable(item):
                await item()
            else:
                yield item
        await asyncio.Event().wait()


@pytest.fixture(autouse=True)
def fast_hangup(monkeypatch):
    monkeypatch.setattr(bridge, "AUDIO_QUIET_SECONDS", 0.05)
    monkeypatch.setattr(bridge, "CLOSING_AUDIO_WAIT_SECONDS", 0.5)


def use_agent(monkeypatch, agent):
    fake_client = SimpleNamespace(agent=SimpleNamespace(v1=SimpleNamespace(connect=lambda: agent)))
    monkeypatch.setattr(bridge, "dg_client", fake_client)


def run(coro):
    return asyncio.run(asyncio.wait_for(coro, timeout=5))


def hangup_marks(twilio):
    return [name for name in twilio.marks() if name.startswith("hangup")]


def test_hangs_up_after_the_goodbye_has_played(monkeypatch):
    twilio = FakeTwilio()

    async def caller_speaks():
        twilio.inbound.put_nowait({"event": "media", "media": {"payload": "AAAA"}})

    agent = FakeAgent([
        text("assistant", "How can I help you?"),
        caller_speaks,
        text("user", "My sink is leaking."),
        text("assistant", "Thanks, Sam. I've got a leaking sink at 214 Eddy, apartment 3."),
        b"\xff" * 400,
        text("assistant", "Our on-call team has your request and will call you back. If anyone is in danger, call 911."),
        text("assistant", "Goodbye."),
        b"\xff" * 320,
        message("AgentAudioDone"),
    ])
    use_agent(monkeypatch, agent)
    session = CallSession()

    run(bridge.run_bridge(twilio, session))

    assert agent.settings is not None
    assert agent.media == [b"\x00\x00\x00"]
    assert [frame["event"] for frame in twilio.sent].count("media") == 5  # 400 + 320 bytes in 160-byte frames
    # The hang-up mark goes after all of the goodbye's audio, and it's the one that ended the call.
    assert twilio.sent[-1]["event"] == "mark"
    assert hangup_marks(twilio) == ["hangup-2"]
    assert session.call_sid == "CA1" and session.from_number == "+16075550199"
    assert session.transcript_text.endswith("Agent: Goodbye.")


def test_does_not_trust_a_mark_that_more_audio_followed(monkeypatch):
    # Timeline: audio at 0, mark 1 at ~0.3, more audio at 0.4, mark 1's echo at ~0.5, mark 2 at ~0.7.
    monkeypatch.setattr(bridge, "AUDIO_QUIET_SECONDS", 0.3)
    monkeypatch.setattr(bridge, "HANGUP_POLL_SECONDS", 0.02)
    twilio = FakeTwilio(echo_delay=0.2)
    use_agent(monkeypatch, FakeAgent([text("assistant", "Goodbye."), b"\xff" * 160, pause(0.4), b"\xff" * 160]))

    run(bridge.run_bridge(twilio, CallSession()))

    # Mark 1's echo came after more audio was sent, so it was ignored and mark 2 was needed.
    assert hangup_marks(twilio) == ["hangup-1", "hangup-2"]


def test_hangs_up_when_the_goodbye_audio_came_before_its_text(monkeypatch):
    twilio = FakeTwilio()
    use_agent(monkeypatch, FakeAgent([b"\xff" * 160, text("assistant", "Goodbye.")]))

    run(bridge.run_bridge(twilio, CallSession()))

    assert hangup_marks(twilio) == ["hangup-1"]


def test_hangs_up_even_if_twilio_never_confirms(monkeypatch):
    monkeypatch.setattr(bridge, "HANGUP_TIMEOUT_SECONDS", 0.6)
    twilio = FakeTwilio(echo_delay=None)
    use_agent(monkeypatch, FakeAgent([text("assistant", "Goodbye."), b"\xff" * 160]))

    run(bridge.run_bridge(twilio, CallSession()))

    assert hangup_marks(twilio) == ["hangup-1"]


def test_the_caller_saying_goodbye_does_not_hang_up(monkeypatch):
    twilio = FakeTwilio()

    async def caller_hangs_up():
        twilio.inbound.put_nowait({"event": "stop"})

    use_agent(monkeypatch, FakeAgent([text("user", "Okay, goodbye."), b"\xff" * 160, pause(0.8), caller_hangs_up]))

    run(bridge.run_bridge(twilio, CallSession()))

    assert hangup_marks(twilio) == []


def test_a_caller_hanging_up_ends_the_bridge(monkeypatch):
    twilio = FakeTwilio()

    async def caller_hangs_up():
        twilio.inbound.put_nowait({"event": "stop"})

    use_agent(monkeypatch, FakeAgent([text("assistant", "How can I help you?"), caller_hangs_up]))
    session = CallSession()

    run(bridge.run_bridge(twilio, session))

    assert session.transcript == [("assistant", "How can I help you?")]
    assert hangup_marks(twilio) == []


def test_rejects_a_stream_with_a_forged_token(monkeypatch):
    use_agent(monkeypatch, None)  # never connected
    with pytest.raises(bridge.StreamRejected):
        run(bridge.run_bridge(FakeTwilio(token="forged"), CallSession()))
