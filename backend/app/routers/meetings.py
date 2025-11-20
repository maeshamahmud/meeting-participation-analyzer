from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Literal
from uuid import uuid4

from app.services.recall import create_meeting_bot, RecallAIError

router = APIRouter(prefix="/api/meetings", tags=["meetings"])

# In-memory store for now (MVP)
MEETINGS_DB: dict[str, dict] = {}


class CreateMeetingRequest(BaseModel):
    title: str
    provider: Literal["zoom", "gmeet", "teams"]
    meeting_url: HttpUrl


class MeetingResponse(BaseModel):
    id: str
    title: str
    provider: str
    meeting_url: HttpUrl
    status: str
    recall_bot_id: str | None = None


@router.post("", response_model=MeetingResponse)
async def create_meeting(payload: CreateMeetingRequest):
    # 1. Call Recall.ai to create a meeting bot
    try:
        bot_resp = await create_meeting_bot(
            meeting_url=str(payload.meeting_url),
            name=payload.title,
        )
    except RecallAIError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        # unexpected error
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

    # The response structure may differ; adjust the key name.
    recall_bot_id = bot_resp.get("id") or bot_resp.get("bot_id")

    meeting_id = str(uuid4())
    meeting = {
        "id": meeting_id,
        "title": payload.title,
        "provider": payload.provider,
        "meeting_url": str(payload.meeting_url),
        "status": "created",  # later: scheduled / in_progress / completed
        "recall_bot_id": recall_bot_id,
    }

    MEETINGS_DB[meeting_id] = meeting
    return meeting


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(meeting_id: str):
    meeting = MEETINGS_DB.get(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

