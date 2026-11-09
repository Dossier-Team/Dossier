import asyncio
import json
from datetime import datetime, timezone

import httpx

import src.extraction.service as service
from src.agent.session import CallSession
from src.delivery.dossier import call_payload, send_to_dossier
from src.schemas.extraction import MaintenanceCall

SESSION = CallSession(
    call_sid="CA1",
    from_number="+16075550199",
    to_number="+16075550100",
    transcript=[("assistant", "How can I help you?"), ("user", "My sink is leaking.")],
    started_at=datetime(2026, 11, 9, 15, 0, tzinfo=timezone.utc),
    ended_at=datetime(2026, 11, 9, 15, 2, tzinfo=timezone.utc),
)
DETAILS = MaintenanceCall(caller_name="Sam Rivera", address="214 Eddy St, apt 3", problem="Sink is leaking.",
                          email="sam@example.com", email_confirmed=True)


def test_payload_has_the_transcript_by_speaker_and_the_details():
    payload = call_payload(SESSION, DETAILS)
    assert payload["call_sid"] == "CA1"
    assert payload["from_number"] == "+16075550199"
    assert payload["started_at"] == "2026-11-09T15:00:00+00:00"
    assert payload["transcript"] == [
        {"speaker": "Agent", "text": "How can I help you?"},
        {"speaker": "Caller", "text": "My sink is leaking."},
    ]
    assert payload["details"]["caller_name"] == "Sam Rivera"
    assert payload["details"]["email_confirmed"] is True
    assert call_payload(SESSION, None)["details"] is None


def responder(*statuses):
    calls = []

    def handle(request: httpx.Request):
        calls.append(request)
        status = statuses[min(len(calls), len(statuses)) - 1]
        if status == "drop":
            raise httpx.ConnectError("connection refused")
        return httpx.Response(status, json={"ok": status < 300})

    return httpx.MockTransport(handle), calls


def send(transport):
    return asyncio.run(send_to_dossier({"call_sid": "CA1"}, url="https://dossier.test/call", token="tok",
                                       delays=(0, 0), transport=transport))


def test_sends_with_the_token():
    transport, calls = responder(200)
    assert send(transport)
    assert len(calls) == 1
    assert calls[0].headers["authorization"] == "Bearer tok"
    assert json.loads(calls[0].content) == {"call_sid": "CA1"}


def test_retries_a_server_error_or_a_dropped_connection():
    transport, calls = responder(503, "drop", 200)
    assert send(transport)
    assert len(calls) == 3


def test_gives_up_after_three_tries():
    transport, calls = responder(500)
    assert not send(transport)
    assert len(calls) == 3


def test_does_not_retry_a_rejection():
    transport, calls = responder(401)
    assert not send(transport)
    assert len(calls) == 1


def test_still_sends_the_transcript_when_extraction_fails(monkeypatch):
    sent = []

    async def broken(_text):
        raise RuntimeError("Gemini is down")

    async def capture(payload):
        sent.append(payload)
        return True

    monkeypatch.setattr(service, "run_extraction_on_transcript", broken)
    monkeypatch.setattr(service, "send_to_dossier", capture)
    asyncio.run(service.process_finished_call(SESSION))
    assert sent[0]["details"] is None
    assert len(sent[0]["transcript"]) == 2


def test_says_a_call_started_once_with_the_token():
    from src.delivery.dossier import send_call_status

    transport, calls = responder(200)
    assert asyncio.run(send_call_status("CA1", "+16075550199", "started", url="https://dossier.test/call", token="tok", transport=transport))
    assert len(calls) == 1
    assert str(calls[0].url) == "https://dossier.test/call/status"
    assert calls[0].headers["authorization"] == "Bearer tok"
    assert json.loads(calls[0].content) == {"call_sid": "CA1", "from_number": "+16075550199", "status": "started"}


def test_a_missed_call_status_is_not_retried_or_raised():
    from src.delivery.dossier import send_call_status

    transport, calls = responder("drop")
    assert not asyncio.run(send_call_status("CA1", None, "started", url="https://dossier.test/call", token="tok", transport=transport))
    assert len(calls) == 1
