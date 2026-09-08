from fastapi import FastAPI

from src.routes.twilio_routes import router as twilio_router

app = FastAPI()
app.include_router(twilio_router)

@app.get("/")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)