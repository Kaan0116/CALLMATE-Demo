from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Integer, JSON, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class CustomerProfile(Base):
    __tablename__ = "customer_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    phone_hash = Column(String(64), nullable=True, index=True)  # SHA-256 of phone — KVKK compliant

    # Personality profile (MBTI-style)
    personality_type = Column(String(50), nullable=True)  # impatient, detail_oriented, emotional, rational
    patience_score = Column(Float, default=0.5)
    aggressiveness_score = Column(Float, default=0.0)
    emotionality_score = Column(Float, default=0.5)
    detail_orientation = Column(Float, default=0.5)

    # Behavioral signals
    avg_call_duration = Column(Float, nullable=True)
    total_calls = Column(Integer, default=0)
    complaint_rate = Column(Float, default=0.0)
    satisfaction_score = Column(Float, nullable=True)
    dominant_intent = Column(String(50), nullable=True)  # complaint, purchase, inquiry

    # Vector embedding stored in Qdrant; ID reference here
    qdrant_point_id = Column(String(64), nullable=True, unique=True)

    # Last interaction context
    last_emotion = Column(String(50), nullable=True)
    last_call_at = Column(DateTime(timezone=True), nullable=True)

    tags = Column(JSON, default=[])
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    company = relationship("Company", back_populates="customer_profiles")
    calls = relationship("Call", back_populates="customer")


class PerformanceScore(Base):
    __tablename__ = "performance_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    operator_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    period_date = Column(DateTime(timezone=True), nullable=False)
    period_type = Column(String(20), default="daily")  # daily, weekly, monthly

    total_calls = Column(Integer, default=0)
    avg_call_duration = Column(Float, nullable=True)
    avg_quality_score = Column(Float, nullable=True)
    emotion_score = Column(Float, nullable=True)
    procedure_compliance = Column(Float, nullable=True)
    coaching_acknowledgment_rate = Column(Float, nullable=True)
    customer_satisfaction = Column(Float, nullable=True)
    composite_score = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    operator = relationship("User", back_populates="performance_scores")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    company_id = Column(UUID(as_uuid=True), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(String(64), nullable=True)
    ip_address = Column(String(45), nullable=True)
    details = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="audit_logs")
