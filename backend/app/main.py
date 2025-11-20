from fastapi import FastAPI
from app.routers import meetings  # 👈 import router

app = FastAPI(title="Meeting Participation Analyzer API")

# 👇 register router so /api/meetings exists
app.include_router(meetings.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
