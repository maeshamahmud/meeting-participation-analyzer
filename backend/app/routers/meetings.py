from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Literal, Optional
from uuid import uuid4
from app.services.recall import create_meeting_bot, get_meeting_bot, RecallAIError
from app.routers.recall_webhook import register_bot
from app.routers.recall_webhook import MEETING_TALK_TIME

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
    recall_bot_status: Optional[str] = None  

class ParticipantStats(BaseModel):
    participant_id: str
    talk_seconds: float
    percentage: float

class ParticipationResponse(BaseModel):
    meeting_id: str
    total_talk_seconds: float
    participants: list[ParticipantStats]

@router.post("", response_model=MeetingResponse)
async def create_meeting(payload: CreateMeetingRequest) -> MeetingResponse:
    try:
        bot_resp = await create_meeting_bot(
            meeting_url=str(payload.meeting_url),
            bot_name=payload.title,
        )
    except RecallAIError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    recall_bot_id = bot_resp.get("id")

    meeting_id = str(uuid4())
    meeting_id = str(uuid4())
    meeting = {
        "id": meeting_id,
        "title": payload.title,
        "provider": payload.provider,
        "meeting_url": str(payload.meeting_url),
        "status": "created",
        "recall_bot_id": recall_bot_id,
        "recall_bot_status": recall_bot_status,
    }

    MEETINGS_DB[meeting_id] = meeting

    if recall_bot_id:
        register_bot(meeting_id, recall_bot_id)

    return MeetingResponse(**meeting)

@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(meeting_id: str) -> MeetingResponse:
    meeting = MEETINGS_DB.get(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    bot_id = meeting.get("recall_bot_id")
    if bot_id:
        try:
            bot_info = await get_meeting_bot(bot_id)
            meeting["recall_bot_status"] = bot_info.get("status")
        except RecallAIError:
            # ignore status errors for now, keep old status
            pass

    return MeetingResponse(**meeting)

@router.get("/{meeting_id}/participation", response_model=ParticipationResponse)
async def get_participation(meeting_id: str) -> ParticipationResponse:
    stats = MEETING_TALK_TIME.get(meeting_id, {})
    total = sum(stats.values()) or 1e-9  # avoid divide by zero

    participants = [
        ParticipantStats(
            participant_id=pid,
            talk_seconds=secs,
            percentage=(secs / total) * 100.0,
        )
        for pid, secs in stats.items()
    ]

    return ParticipationResponse(
        meeting_id=meeting_id,
        total_talk_seconds=total,
        participants=participants,
    )

