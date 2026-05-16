import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Text, Enum as SAEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class CoachingType(str, enum.Enum):
    tone_warning = "tone_warning"
    script_suggestion = "script_suggestion"
    sales_opportunity = "sales_opportunity"
    procedure_step = "procedure_step"
    profanity_alert = "profanity_alert"
    pause_suggestion = "pause_suggestion"


class CoachingEvent(Base):
    __tablename__ = "coaching_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    call_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("calls.id"), nullable=False)
    coaching_type: Mapped[CoachingType] = mapped_column(SAEnum(CoachingType), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    suggested_phrase: Mapped[str | None] = mapped_column(Text, nullable=True)
    urgency: Mapped[str] = mapped_column(String(20), default="normal")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    was_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)

    call: Mapped["Call"] = relationship("Call", back_populates="coaching_events")
