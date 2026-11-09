import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

import app as app_module
import src.agent.bridge as bridge
from src.telephony.security import stream_token, twilio_signature

TOKEN = "test-twilio-token"
PARAMS = {"CallSid": "CA123", "From": "+16075550199", "To": "+16075550100", "AccountSid": "AC1"}

client = TestClient(app_module.app)


def test_has_no_public_docs_pages():
    for path in ("/docs", "/redoc", "/openapi.json"):
        assert client.get(path).status_code == 404
    assert client.get("/").json() == {"status": "ok"}


def test_rejects_an_unsigned_inbound_call():
    assert client.post("/twiml", data=PARAMS).status_code == 403
    bad = client.post("/twiml", data=PARAMS, headers={"X-Twilio-Signature": "nope"})
    assert bad.status_code == 403


def test_answers_a_signed_call_with_a_stream_carrying_its_token():
    signature = twilio_signature(TOKEN, "https://voice.example.org/twiml", PARAMS)
    response = client.post("/twiml", data=PARAMS, headers={"X-Twilio-Signature": signature})
    assert response.status_code == 200
    xml = response.text
    assert '<Stream url="wss://voice.example.org/media">' in xml
    assert f'<Parameter name="token" value="{stream_token(TOKEN, "CA123")}" />' in xml
    assert '<Parameter name="from" value="+16075550199" />' in xml
    assert xml.index("</Connect>") < xml.index("<Hangup />")


def test_media_socket_rejects_a_stream_without_our_token(monkeypatch):
    def connect():
        raise AssertionError("Deepgram must not be reached for a rejected stream")

    monkeypatch.setattr(bridge.dg_client.agent.v1, "connect", connect)
    with client.websocket_connect("/media") as ws:
        ws.send_json({"event": "connected"})
        ws.send_json({"event": "start", "start": {"streamSid": "MZ1", "customParameters": {"callSid": "CA123", "token": "forged"}}})
        with pytest.raises(WebSocketDisconnect) as closed:
            ws.receive_text()
    assert closed.value.code == 1008
