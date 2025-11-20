from fastapi import FastAPI
from app.routers import meetings

app = FastAPI(title="Meeting Participation Analyzer API")

app.include_router(meetings.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}

