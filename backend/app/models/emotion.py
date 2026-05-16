import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Float, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class EmotionType(str, enum.Enum):
    happy = "happy"
    angry = "angry"
    stressed = "stressed"
    neutral = "neutral"
    sad = "sad"
    excited = "excited"


class EmotionEvent(Base):
    __tablename__ = "emotions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    call_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("calls.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    emotion: Mapped[EmotionType] = mapped_column(SAEnum(EmotionType), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    valence: Mapped[float | None] = mapped_column(Float, nullable=True)
    arousal: Mapped[float | None] = mapped_column(Float, nullable=True)
    pitch_hz: Mapped[float | None] = mapped_column(Float, nullable=True)
    energy_db: Mapped[float | None] = mapped_column(Float, nullable=True)
    speech_rate_wpm: Mapped[float | None] = mapped_column(Float, nullable=True)

    call: Mapped["Call"] = relationship("Call", back_populates="emotions")
