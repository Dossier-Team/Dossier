import os

from dotenv import load_dotenv
from elevenlabs import ElevenLabs
from fastapi import FastAPI, Request
from fastapi.responses import Response

from tools import router as tools_router


load_dotenv()

app = FastAPI()
app.include_router(tools_router)

elevenlabs = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
AGENT_ID = os.environ["ELEVENLABS_AGENT_ID"]


@app.post("/twilio/inbound")
async def handle_inbound_call(request: Request):
    form = await request.form()
    from_number = form.get("From")
    to_number = form.get("To")

    twiml = elevenlabs.conversational_ai.twilio.register_call(
        agent_id=AGENT_ID,
        from_number=from_number,
        to_number=to_number,
        direction="inbound",
    )

    return Response(content=twiml, media_type="application/xml")


@app.post("/elevenlabs-webhook")
async def elevenlabs_webhook(request: Request):
    return Response(status_code=200)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
