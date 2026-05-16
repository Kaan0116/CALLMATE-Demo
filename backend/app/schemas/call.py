from pydantic import BaseModel
from datetime import datetime
import uuid


class CallStartRequest(BaseModel):
    phone_number: str | None = None
    is_autonomous: bool = False


class CallStartResponse(BaseModel):
    call_id: uuid.UUID
    websocket_url: str
    coaching_websocket_url: str
    started_at: datetime


class CallEndRequest(BaseModel):
    call_id: uuid.UUID


class CallSummary(BaseModel):
    id: uuid.UUID
    status: str
    started_at: datetime
    ended_at: datetime | None
    duration_seconds: int | None
    overall_sentiment_score: float | None
    quality_score: float | None
    operator_id: uuid.UUID

    model_config = {"from_attributes": True}


class CallDetail(CallSummary):
    transcripts: list[dict] = []
    emotions: list[dict] = []
    coaching_events: list[dict] = []
