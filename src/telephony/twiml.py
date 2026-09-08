"""TwiML documents returned to Twilio's inbound-call webhook."""

from xml.sax.saxutils import quoteattr


def build_stream_twiml(
    host: str,
    call_sid: str | None = None,
    from_number: str | None = None,
    to_number: str | None = None,
) -> str:
    """TwiML that hands the call's audio to our media socket.

    The `<Parameter>`s are the only channel for call metadata: the media
    WebSocket carries no Twilio headers, so without them every extraction
    lands anonymous.
    """
    parameters = {
        "callSid": call_sid,
        "from": from_number,
        "to": to_number,
    }
    parameter_tags = "\n".join(
        f"      <Parameter name={quoteattr(name)} value={quoteattr(value)} />"
        for name, value in parameters.items()
        if value
    )
    stream_url = quoteattr(f"wss://{host}/media")
    stream = (
        f"    <Stream url={stream_url}>\n{parameter_tags}\n    </Stream>"
        if parameter_tags
        else f"    <Stream url={stream_url} />"
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<Response>\n"
        "  <Connect>\n"
        f"{stream}\n"
        "  </Connect>\n"
        "</Response>"
    )
