import httpx
from typing import Optional

from app.config import settings


class RecallAIError(Exception):
    """Custom exception for Recall.ai-related errors."""
    pass


async def create_meeting_bot(
    meeting_url: str,
    *,
    bot_name: Optional[str] = None,
) -> dict:
    """
    Create a Recall.ai meeting bot for the given meeting URL.
    """
    base_url = f"https://{settings.recall_region}.recall.ai"
    url = f"{base_url}/api/v1/bot"

    # Minimal valid payload: only meeting_url and optional bot_name
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
        raise RecallAIError(f"Recall.ai error {resp.status_code}: {resp.text}")

    return resp.json()


async def get_meeting_bot(bot_id: str) -> dict:
    """
    Fetch the current status/info for a Recall.ai meeting bot.
    """
    base_url = f"https://{settings.recall_region}.recall.ai"
    url = f"{base_url}/api/v1/bot/{bot_id}"

    headers = {
        "Authorization": f"Token {settings.recall_api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, headers=headers)

    if resp.status_code >= 400:
        raise RecallAIError(f"Recall.ai error {resp.status_code}: {resp.text}")

    return resp.json()
