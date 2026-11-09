from src.telephony.security import is_from_twilio, is_valid_stream_token, stream_token, twilio_signature

URL = "https://mycompany.com/myapp.php?foo=1&bar=2"
PARAMS = {"CallSid": "CA1234567890ABCDE", "Caller": "+12349013030", "Digits": "1234", "From": "+12349013030", "To": "+18005551212"}


def test_signs_like_twilio():
    # The vector twilio-node's own webhook tests use.
    assert twilio_signature("12345", URL, PARAMS) == "0/KCTR6DLpKmkAf8muzZqo1nDgQ="


def test_accepts_only_a_matching_signature():
    signature = twilio_signature("12345", URL, PARAMS)
    assert is_from_twilio("12345", URL, PARAMS, signature)
    assert not is_from_twilio("12345", URL, {**PARAMS, "Digits": "9"}, signature)
    assert not is_from_twilio("other", URL, PARAMS, signature)
    assert not is_from_twilio("12345", URL, PARAMS, None)


def test_stream_token_is_tied_to_the_call_and_the_auth_token():
    token = stream_token("secret", "CA1")
    assert is_valid_stream_token("secret", "CA1", token)
    assert not is_valid_stream_token("secret", "CA2", token)
    assert not is_valid_stream_token("other", "CA1", token)
    assert not is_valid_stream_token("secret", "CA1", None)
    assert not is_valid_stream_token("secret", None, token)
