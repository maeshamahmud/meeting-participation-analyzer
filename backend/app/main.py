from fastapi import FastAPI
from app.routers import meetings, recall_webhook

app = FastAPI(title="Meeting Participation Analyzer API")

app.include_router(meetings.router)
app.include_router(recall_webhook.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
