import logging

from fastapi import FastAPI

from src.routes.twilio_routes import router as twilio_router

# Each call's progress (started, ended, sent to Dossier) is logged at INFO.
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')

app = FastAPI()
app.include_router(twilio_router)

@app.get("/")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)