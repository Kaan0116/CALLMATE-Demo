import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, JSON, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class CustomerProfile(Base):
    __tablename__ = "customer_profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    phone_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    personality_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    personality_traits: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    preferred_communication: Mapped[str | None] = mapped_column(String(50), nullable=True)
    avg_satisfaction_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_calls: Mapped[int] = mapped_column(Integer, default=0)
    last_call_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    embedding_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    calls: Mapped[list["Call"]] = relationship("Call", back_populates="customer")
