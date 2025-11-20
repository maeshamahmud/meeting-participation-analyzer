from fastapi import APIRouter, Request
from typing import Dict, Any, DefaultDict
from collections import defaultdict

router = APIRouter(prefix="/api/recall", tags=["recall"])

# Simple in-memory stats: keyed by our meeting_id
# meeting_id -> { participant_id -> total_seconds }
MEETING_TALK_TIME: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))

# Map recall_bot_id -> our meeting_id (we'll fill this from MEETINGS_DB)
BOT_TO_MEETING: Dict[str, str] = {}


def register_bot(meeting_id: str, bot_id: str):
    BOT_TO_MEETING[bot_id] = meeting_id


@router.post("/webhook")
async def recall_webhook(request: Request):
    payload: Dict[str, Any] = await request.json()

    event = payload.get("event")
    if event != "transcript.data":
        # ignore other events for now
        return {"status": "ignored", "event": event}

    data = payload.get("data", {})
    inner = data.get("data", {})

    words = inner.get("words") or []
    participant = inner.get("participant") or {}

    # You'll need to confirm from docs whether this is data["bot_id"] or data["bot"]["id"]
    bot_id = data.get("bot_id") or data.get("bot", {}).get("id")
    if not bot_id or not words:
        return {"status": "ignored", "reason": "missing bot_id or words"}

    meeting_id = BOT_TO_MEETING.get(bot_id)
    if not meeting_id:
        # We don't know which meeting this belongs to yet
        return {"status": "ignored", "reason": "unknown bot_id"}

    participant_id = str(participant.get("id") or "unknown")

    # Approximate utterance duration from first/last word timestamps
    try:
        start = float(words[0]["start_timestamp"]["relative"])
        last = words[-1]
        end = last.get("end_timestamp", {}).get("relative")
        if end is None:
            end = float(last["start_timestamp"]["relative"])
        duration = max(0.0, float(end) - start)
    except Exception:
        duration = 0.0

    MEETING_TALK_TIME[meeting_id][participant_id] += duration

    return {"status": "ok"}
