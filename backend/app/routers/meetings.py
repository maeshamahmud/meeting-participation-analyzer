cat > app/routers/meetings.py << 'EOF'
from fastapi import APIRouter
from pydantic import BaseModel, HttpUrl
from typing import Literal
from uuid import uuid4

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


@router.post("", response_model=MeetingResponse)
async def create_meeting(payload: CreateMeetingRequest):
    meeting_id = str(uuid4())
    # Later: call Recall.ai create bot here

    meeting = {
        "id": meeting_id,
        "title": payload.title,
        "provider": payload.provider,
        "meeting_url": str(payload.meeting_url),
        "status": "created",  # later: scheduled / in_progress / completed
    }
    MEETINGS_DB[meeting_id] = meeting
    return meeting


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(meeting_id: str):
    meeting = MEETINGS_DB.get(meeting_id)
    if not meeting:
        # Avoid importing HTTPException yet; but you *can* if you want 404.
        return MeetingResponse(
            id="",
            title="Not found",
            provider="zoom",
            meeting_url="https://example.com",
            status="not_found",
        )
    return meeting
EOF
