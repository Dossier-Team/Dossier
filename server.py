from fastapi import FastAPI

from src.routes.elevenlabs_routes import router as elevenlabs_router
from src.routes.tools_routes import router as tools_router
from src.routes.twilio_routes import router as twilio_router
app = FastAPI()
app.include_router(elevenlabs_router)
app.include_router(twilio_router)
app.include_router(tools_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
