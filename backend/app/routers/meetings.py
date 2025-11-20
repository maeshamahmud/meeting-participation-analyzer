from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Literal, Optional
from uuid import uuid4

from app.services.recall import create_meeting_bot, RecallAIError

router = APIRouter(prefix="/api/meetings", tags=["meetings"])

# simple in-memory store for now
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
    recall_bot_id: Optional[str] = None


@router.post("", response_model=MeetingResponse)
async def create_meeting(payload: CreateMeetingRequest) -> MeetingResponse:
    # 1. Ask Recall.ai to create a bot for this meeting
    try:
        bot_resp = await create_meeting_bot(
            meeting_url=str(payload.meeting_url),
            bot_name=payload.title,
        )
    except RecallAIError as e:
        # Something went wrong on Recall side
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        # Unexpected error
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

    # Bot ID comes back in "id" (per docs)
    recall_bot_id = bot_resp.get("id")

    # 2. Save meeting in our (temporary) in-memory DB
    meeting_id = str(uuid4())
    meeting = {
        "id": meeting_id,
        "title": payload.title,
        "provider": payload.provider,
        "meeting_url": str(payload.meeting_url),
        "status": "created",
        "recall_bot_id": recall_bot_id,
    }

    MEETINGS_DB[meeting_id] = meeting

    # 3. Return response object
    return MeetingResponse(**meeting)


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(meeting_id: str) -> MeetingResponse:
    meeting = MEETINGS_DB.get(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return MeetingResponse(**meeting)
