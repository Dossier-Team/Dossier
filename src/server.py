import os
from datetime import datetime

from dotenv import load_dotenv
from elevenlabs import ElevenLabs
from elevenlabs.errors import BadRequestError
from fastapi import FastAPI, Request, Response

from tools import router as tools_router


load_dotenv()

app = FastAPI()
app.include_router(tools_router)

elevenlabs = ElevenLabs(api_key=os.environ['ELEVENLABS_API_KEY'])
AGENT_ID = os.environ['ELEVENLABS_AGENT_ID']
WEBHOOK_SECRET = os.environ['ELEVENLABS_WEBHOOK_SECRET']


@app.post('/twilio/inbound')
async def handle_inbound_call(request: Request) -> Response:
    form = await request.form()
    from_number = form.get('From')
    to_number = form.get('To')

    twiml = elevenlabs.conversational_ai.twilio.register_call(
        agent_id=AGENT_ID,
        from_number=from_number,
        to_number=to_number,
        direction='inbound',
    )

    return Response(content=twiml, media_type='application/xml')


@app.post('/elevenlabs/call-complete')
async def handle_call_complete(request: Request) -> Response:
    raw_body = await request.body()
    signature = request.headers.get("elevenlabs-signature")

    try:
        event = elevenlabs.webhooks.construct_event(
            rawBody=raw_body.decode("utf-8"),
            sig_header=signature,
            secret=WEBHOOK_SECRET,
        )
    except BadRequestError:
        return Response(status_code=401)

    if event.get("type") != "post_call_transcription":
        return Response(status_code=200)  # ack it, just not what we handle here

    data = event.get("data", {})

    call_id = data.get("conversation_id")
    transcript = data.get("transcript")
    start_time_unix_secs = data.get("metadata", {}).get("start_time_unix_secs")
    call_date = (
        datetime.fromtimestamp(start_time_unix_secs)
        if start_time_unix_secs is not None
        else None
    )

    # ... do something with call_id / transcript / call_date

    return Response(status_code=200)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
