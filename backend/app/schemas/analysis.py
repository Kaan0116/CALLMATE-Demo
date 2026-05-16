from pydantic import BaseModel
from datetime import datetime
import uuid


class EmotionSummary(BaseModel):
    call_id: uuid.UUID
    dominant_emotion: str
    avg_valence: float
    avg_arousal: float
    emotion_timeline: list[dict]


class PersonalityCard(BaseModel):
    customer_id: uuid.UUID
    personality_type: str
    traits: dict
    confidence: float
    recommendations: list[str]
    total_calls: int
    last_call_at: datetime | None


class RecommendationList(BaseModel):
    call_id: uuid.UUID
    coaching_events: list[dict]
    pending_count: int
