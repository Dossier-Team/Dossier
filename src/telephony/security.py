"""Proof that a request really came from Twilio.

The inbound-call webhook carries Twilio's `X-Twilio-Signature`, checked here
against the account's auth token. That webhook then hands out a per-call stream
token, so the media socket only accepts streams this server started.

https://www.twilio.com/docs/usage/webhooks/webhooks-security
"""

import base64
import hashlib
import hmac


def twilio_signature(auth_token: str, url: str, params: dict[str, str]) -> str:
    """HMAC-SHA1 of the full URL followed by each POST parameter, sorted by name, base64-encoded."""
    data = url + ''.join(name + params[name] for name in sorted(params))
    digest = hmac.new(auth_token.encode(), data.encode(), hashlib.sha1).digest()
    return base64.b64encode(digest).decode('ascii')


def is_from_twilio(auth_token: str, url: str, params: dict[str, str], signature: str | None) -> bool:
    if not signature:
        return False
    return hmac.compare_digest(twilio_signature(auth_token, url, params), signature)


def stream_token(auth_token: str, call_sid: str) -> str:
    """A token only this server can make, tying a media stream to the call it was started for."""
    return hmac.new(auth_token.encode(), f'stream:{call_sid}'.encode(), hashlib.sha256).hexdigest()


def is_valid_stream_token(auth_token: str, call_sid: str | None, token: str | None) -> bool:
    if not call_sid or not token:
        return False
    return hmac.compare_digest(stream_token(auth_token, call_sid), token)
