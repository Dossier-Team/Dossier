"""Twilio Media Streams wire protocol: encoding and decoding socket frames.

https://www.twilio.com/docs/voice/media-streams/websocket-messages
"""

import base64
import json
from typing import Any

# Inbound events Twilio sends on the media socket.
CONNECTED = "connected"
START = "start"
MEDIA = "media"
DTMF = "dtmf"
MARK = "mark"
STOP = "stop"

# 8 kHz mulaw is one byte per sample, so 160 bytes is a 20 ms frame — the size
# Twilio itself streams and the size it plays back most smoothly.
FRAME_BYTES = 160


def decode_frame(raw: str) -> dict[str, Any]:
    """Parse one inbound text frame from Twilio."""
    return json.loads(raw)


def frame_event(frame: dict[str, Any]) -> str | None:
    return frame.get("event")


def decode_media_payload(frame: dict[str, Any]) -> bytes:
    """Raw mulaw audio out of a `media` frame."""
    return base64.b64decode(frame["media"]["payload"])


def decode_start(frame: dict[str, Any]) -> tuple[str, dict[str, str]]:
    """`(stream_sid, custom_parameters)` out of a `start` frame.

    `customParameters` carries whatever `<Parameter>`s the TwiML declared on
    the `<Stream>` — that is the only way call metadata reaches this socket.
    """
    start = frame["start"]
    return start["streamSid"], start.get("customParameters") or {}


def decode_dtmf_digit(frame: dict[str, Any]) -> str | None:
    return (frame.get("dtmf") or {}).get("digit")


def media_frame(stream_sid: str, payload: bytes) -> str:
    """Outbound audio frame. `payload` must be mulaw/8000, as Twilio expects."""
    return json.dumps(
        {
            "event": "media",
            "streamSid": stream_sid,
            "media": {"payload": base64.b64encode(payload).decode("ascii")},
        }
    )


def clear_frame(stream_sid: str) -> str:
    """Drops everything Twilio has buffered but not yet played — the barge-in signal."""
    return json.dumps({"event": "clear", "streamSid": stream_sid})


def mark_frame(stream_sid: str, name: str) -> str:
    """Asks Twilio to echo back a `mark` once the audio queued so far has played."""
    return json.dumps({"event": "mark", "streamSid": stream_sid, "mark": {"name": name}})


def chunk_audio(audio: bytes, size: int = FRAME_BYTES) -> list[bytes]:
    """Split an agent audio buffer into Twilio-sized frames."""
    return [audio[offset:offset + size] for offset in range(0, len(audio), size)]
