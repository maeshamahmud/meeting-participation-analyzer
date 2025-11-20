import httpx
from typing import Optional
from app.config import settings


class RecallAIError(Exception):
    """Custom exception for Recall.ai-related errors."""


async def create_meeting_bot(
    meeting_url: str,
    *,
    name: Optional[str] = None,
) -> dict:
    """
    Calls Recall.ai's Create Meeting Bot endpoint.

    NOTE: This is a template. You may need to tweak the URL and payload
    to match the latest Recall.ai docs.
    """
    url = f"{settings.recall_api_base_url}/v1/meeting-bots"

    payload = {
        "meeting_url": meeting_url,
    }
    if name:
        payload["name"] = name

    headers = {
        "Authorization": f"Bearer {settings.recall_api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, json=payload, headers=headers)

    if resp.status_code >= 400:
        raise RecallAIError(
            f"Recall.ai error {resp.status_code}: {resp.text}"
        )

    return resp.json()
