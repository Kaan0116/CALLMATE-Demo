import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Text, Float, Integer, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Speaker(str, enum.Enum):
    operator = "operator"
    customer = "customer"
    system = "system"


class Transcript(Base):
    __tablename__ = "transcripts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    call_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("calls.id"), nullable=False)
    speaker: Mapped[Speaker] = mapped_column(SAEnum(Speaker), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    text_masked: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    chunk_index: Mapped[int | None] = mapped_column(Integer, nullable=True)

    call: Mapped["Call"] = relationship("Call", back_populates="transcripts")
