"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-16
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("ip_whitelist", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("admin", "supervisor", "operator", name="userrole"), nullable=False, server_default="operator"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "customer_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("phone_hash", sa.String(64), nullable=False),
        sa.Column("personality_type", sa.String(50), nullable=True),
        sa.Column("personality_traits", postgresql.JSON(), nullable=True),
        sa.Column("preferred_communication", sa.String(50), nullable=True),
        sa.Column("avg_satisfaction_score", sa.Float(), nullable=True),
        sa.Column("total_calls", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_call_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("embedding_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phone_hash"),
    )

    op.create_table(
        "calls",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("operator_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.Enum("active", "completed", "failed", name="callstatus"), nullable=False, server_default="active"),
        sa.Column("phone_number_hash", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("audio_s3_key", sa.Text(), nullable=True),
        sa.Column("overall_sentiment_score", sa.Float(), nullable=True),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column("is_autonomous", sa.Boolean(), nullable=False, server_default="false"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["operator_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["customer_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_calls_company_started", "calls", ["company_id", "started_at"])

    op.create_table(
        "transcripts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("call_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("speaker", sa.Enum("operator", "customer", "system", name="speaker"), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("text_masked", sa.Text(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("chunk_index", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["call_id"], ["calls.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transcripts_call_ts", "transcripts", ["call_id", "timestamp"])

    op.create_table(
        "emotions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("call_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("emotion", sa.Enum("happy", "angry", "stressed", "neutral", "sad", "excited", name="emotiontype"), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("valence", sa.Float(), nullable=True),
        sa.Column("arousal", sa.Float(), nullable=True),
        sa.Column("pitch_hz", sa.Float(), nullable=True),
        sa.Column("energy_db", sa.Float(), nullable=True),
        sa.Column("speech_rate_wpm", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["call_id"], ["calls.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "coaching_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("call_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("coaching_type", sa.Enum("tone_warning", "script_suggestion", "sales_opportunity", "procedure_step", "profanity_alert", "pause_suggestion", name="coachingtype"), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("suggested_phrase", sa.Text(), nullable=True),
        sa.Column("urgency", sa.String(20), nullable=False, server_default="normal"),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("was_acknowledged", sa.Boolean(), nullable=False, server_default="false"),
        sa.ForeignKeyConstraint(["call_id"], ["calls.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "performance_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("operator_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("score_date", sa.Date(), nullable=False),
        sa.Column("avg_call_quality", sa.Float(), nullable=True),
        sa.Column("avg_sentiment_score", sa.Float(), nullable=True),
        sa.Column("total_calls", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("avg_call_duration", sa.Float(), nullable=True),
        sa.Column("coaching_adherence", sa.Float(), nullable=True),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["operator_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("performance_scores")
    op.drop_table("coaching_events")
    op.drop_table("emotions")
    op.drop_table("transcripts")
    op.drop_table("calls")
    op.drop_table("customer_profiles")
    op.drop_table("users")
    op.drop_table("companies")
