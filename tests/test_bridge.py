"""The bridge, with a fake Twilio socket and a fake Deepgram agent."""

import asyncio
import json
from types import SimpleNamespace

import pytest

import src.agent.bridge as bridge
from src.agent.session import CallSession
from src.telephony.security import stream_token


class FakeTwilio:
    """Plays the caller's side. Echoes each mark at once, as if the audio before it finished playing."""

    def __init__(self, call_sid="CA1", token=None):
        self.inbound: asyncio.Queue = asyncio.Queue()
        self.sent: list[dict] = []
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
        if frame["event"] == "mark":
            self.inbound.put_nowait({"event": "mark", "streamSid": "MZ1", "mark": frame["mark"]})

    def marks(self):
        return [frame["mark"]["name"] for frame in self.sent if frame["event"] == "mark"]


class FakeAgent:
    def __init__(self, script):
        self.script = script  # messages, or callables run against the agent when reached
        self.settings = None
        self.media: list[bytes] = []
        self.responses = []
        self.finished = asyncio.Event()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def send_settings(self, settings):
        self.settings = settings

    async def send_media(self, audio):
        self.media.append(audio)

    async def send_function_call_response(self, response):
        self.responses.append(response)

    async def send_keep_alive(self):
        pass

    async def __aiter__(self):
        for item in self.script:
            await asyncio.sleep(0)
            if callable(item):
                await item()
            else:
                yield item
        self.finished.set()
        await asyncio.Event().wait()  # an open socket with nothing more to say


def text(role, content):
    return SimpleNamespace(type="ConversationText", role=role, content=content)


def message(kind):
    return SimpleNamespace(type=kind)


def end_call(call_id="fc1"):
    function = SimpleNamespace(id=call_id, name="end_call", arguments="{}", client_side=True)
    return SimpleNamespace(type="FunctionCallRequest", functions=[function])


def use_agent(monkeypatch, agent):
    fake_client = SimpleNamespace(agent=SimpleNamespace(v1=SimpleNamespace(connect=lambda: agent)))
    monkeypatch.setattr(bridge, "dg_client", fake_client)


def run(coro):
    return asyncio.run(asyncio.wait_for(coro, timeout=5))


def test_hangs_up_after_the_goodbye_has_played(monkeypatch):
    twilio = FakeTwilio()

    async def caller_speaks():
        twilio.inbound.put_nowait({"event": "media", "media": {"payload": "AAAA"}})

    agent = FakeAgent([
        text("assistant", "How can I help you?"),
        caller_speaks,
        text("user", "My sink is leaking."),
        message("AgentStartedSpeaking"),
        text("assistant", "Thanks, Sam. Goodbye."),
        end_call(),  # arrives while the goodbye is still being spoken
        b"\xff" * 400,
        message("AgentAudioDone"),
    ])
    use_agent(monkeypatch, agent)
    session = CallSession()

    run(bridge.run_bridge(twilio, session))

    assert agent.settings is not None
    assert agent.media == [b"\x00\x00\x00"]
    assert [(r.id, r.name) for r in agent.responses] == [("fc1", "end_call")]
    events = [frame["event"] for frame in twilio.sent]
    assert events.count("media") == 3  # 400 bytes in 160-byte frames
    assert twilio.marks()[-1] == "hangup"
    # The goodbye's audio reaches Twilio before the mark that hangs up after it.
    last_media = len(events) - 1 - events[::-1].index("media")
    assert last_media < len(events) - 1 and twilio.sent[-1]["mark"]["name"] == "hangup"
    assert session.call_sid == "CA1" and session.from_number == "+16075550199"
    assert session.transcript_text == "Agent: How can I help you?\nCaller: My sink is leaking.\nAgent: Thanks, Sam. Goodbye."


def test_hangs_up_when_end_call_comes_after_the_audio(monkeypatch):
    monkeypatch.setattr(bridge, "HANGUP_GRACE_SECONDS", 0.01)
    twilio = FakeTwilio()
    agent = FakeAgent([
        message("AgentStartedSpeaking"),
        text("assistant", "Goodbye."),
        message("AgentAudioDone"),
        end_call(),
    ])
    use_agent(monkeypatch, agent)

    run(bridge.run_bridge(twilio, CallSession()))

    assert twilio.marks() == ["agent-audio-done", "hangup"]


def test_hangs_up_even_if_twilio_never_confirms(monkeypatch):
    monkeypatch.setattr(bridge, "HANGUP_GRACE_SECONDS", 0.01)
    monkeypatch.setattr(bridge, "HANGUP_TIMEOUT_SECONDS", 0.05)
    twilio = FakeTwilio()

    async def no_echo(text):
        twilio.sent.append(json.loads(text))

    twilio.send_text = no_echo
    use_agent(monkeypatch, FakeAgent([end_call()]))

    run(bridge.run_bridge(twilio, CallSession()))

    assert twilio.marks() == ["hangup"]


def test_a_caller_hanging_up_ends_the_bridge(monkeypatch):
    twilio = FakeTwilio()

    async def caller_hangs_up():
        twilio.inbound.put_nowait({"event": "stop"})

    agent = FakeAgent([text("assistant", "How can I help you?"), caller_hangs_up])
    use_agent(monkeypatch, agent)
    session = CallSession()

    run(bridge.run_bridge(twilio, session))

    assert agent.responses == []
    assert session.transcript == [("assistant", "How can I help you?")]


def test_rejects_a_stream_with_a_forged_token(monkeypatch):
    use_agent(monkeypatch, None)  # never connected
    with pytest.raises(bridge.StreamRejected):
        run(bridge.run_bridge(FakeTwilio(token="forged"), CallSession()))
