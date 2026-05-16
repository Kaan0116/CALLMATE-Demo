import uuid
from datetime import datetime, date, timezone
from sqlalchemy import DateTime, ForeignKey, Float, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class PerformanceScore(Base):
    __tablename__ = "performance_scores"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    operator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    score_date: Mapped[date] = mapped_column(Date, nullable=False)
    avg_call_quality: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_sentiment_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_calls: Mapped[int] = mapped_column(Integer, default=0)
    avg_call_duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    coaching_adherence: Mapped[float | None] = mapped_column(Float, nullable=True)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    operator: Mapped["User"] = relationship("User", back_populates="performance_scores")
