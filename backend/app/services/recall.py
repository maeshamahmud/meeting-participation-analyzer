import httpx
from typing import Optional

from app.config import settings


class RecallAIError(Exception):
    pass


async def create_meeting_bot(
    meeting_url: str,
    *,
    bot_name: Optional[str] = None,
) -> dict:
    base_url = f"https://{settings.recall_region}.recall.ai"
    url = f"{base_url}/api/v1/bot"

    payload: dict = {
        "meeting_url": meeting_url,
    }
    if bot_name:
        payload["bot_name"] = bot_name

    headers = {
        "Authorization": f"Token {settings.recall_api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(url, json=payload, headers=headers)

    if resp.status_code >= 400:
        # Surface full body so we can see future issues
        raise RecallAIError(f"Recall.ai error {resp.status_code}: {resp.text}")

    return resp.json()
