from pydantic import BaseModel
from datetime import date
import uuid


class DailyReport(BaseModel):
    report_date: date
    total_calls: int
    avg_duration_seconds: float
    avg_quality_score: float
    avg_sentiment_score: float
    top_emotions: dict
    top_intents: dict


class OperatorReport(BaseModel):
    operator_id: uuid.UUID
    operator_name: str
    period_start: date
    period_end: date
    total_calls: int
    avg_quality_score: float
    avg_sentiment_score: float
    coaching_adherence: float
