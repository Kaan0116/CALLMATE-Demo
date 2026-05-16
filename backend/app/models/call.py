import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Enum as SAEnum, Float, Integer, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class CallStatus(str, enum.Enum):
    active = "active"
    completed = "completed"
    failed = "failed"


class Call(Base):
    __tablename__ = "calls"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    operator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    customer_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("customer_profiles.id"), nullable=True)
    status: Mapped[CallStatus] = mapped_column(SAEnum(CallStatus), default=CallStatus.active)
    phone_number_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    audio_s3_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    overall_sentiment_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_autonomous: Mapped[bool] = mapped_column(Boolean, default=False)

    company: Mapped["Company"] = relationship("Company", back_populates="calls")
    operator: Mapped["User"] = relationship("User", back_populates="calls")
    customer: Mapped["CustomerProfile | None"] = relationship("CustomerProfile", back_populates="calls")
    transcripts: Mapped[list["Transcript"]] = relationship("Transcript", back_populates="call", order_by="Transcript.timestamp")
    emotions: Mapped[list["EmotionEvent"]] = relationship("EmotionEvent", back_populates="call")
    coaching_events: Mapped[list["CoachingEvent"]] = relationship("CoachingEvent", back_populates="call")
