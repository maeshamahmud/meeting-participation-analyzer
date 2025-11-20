from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Literal
from uuid import uuid4

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


@router.post("", response_model=MeetingResponse)
async def create_meeting(payload: CreateMeetingRequest) -> MeetingResponse:
    meeting_id = str(uuid4())

    meeting = {
        "id": meeting_id,
        "title": payload.title,
        "provider": payload.provider,
        "meeting_url": str(payload.meeting_url),
        "status": "created",
    }

    MEETINGS_DB[meeting_id] = meeting
    # return an actual object/dict, not None
    return MeetingResponse(**meeting)


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(meeting_id: str) -> MeetingResponse:
    meeting = MEETINGS_DB.get(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return MeetingResponse(**meeting)
