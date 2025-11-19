from fastapi import FastAPI

app = FastAPI(title="Meeting Participation Analyzer API")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
