import uuid
from datetime import date, timedelta
from collections import Counter
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.base import get_db
from app.models.call import Call, CallStatus
from app.models.emotion import EmotionEvent
from app.models.performance import PerformanceScore
from app.models.user import User
from app.schemas.report import DailyReport, OperatorReport
from app.api.deps import get_current_user, require_supervisor
import io

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/daily", response_model=DailyReport)
async def daily_report(
    report_date: date = Query(default_factory=date.today),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor),
):
    next_day = report_date + timedelta(days=1)
    calls_q = await db.execute(
        select(Call).where(
            Call.company_id == current_user.company_id,
            Call.started_at >= report_date.isoformat(),
            Call.started_at < next_day.isoformat(),
            Call.status == CallStatus.completed,
        )
    )
    calls = calls_q.scalars().all()

    if not calls:
        return DailyReport(
            report_date=report_date,
            total_calls=0, avg_duration_seconds=0.0,
            avg_quality_score=0.0, avg_sentiment_score=0.0,
            top_emotions={}, top_intents={},
        )

    call_ids = [c.id for c in calls]
    emotions_q = await db.execute(select(EmotionEvent).where(EmotionEvent.call_id.in_(call_ids)))
    emotions = emotions_q.scalars().all()
    emotion_counts = Counter(e.emotion for e in emotions)

    durations = [c.duration_seconds or 0 for c in calls]
    qualities = [c.quality_score for c in calls if c.quality_score is not None]
    sentiments = [c.overall_sentiment_score for c in calls if c.overall_sentiment_score is not None]

    return DailyReport(
        report_date=report_date,
        total_calls=len(calls),
        avg_duration_seconds=sum(durations) / len(durations),
        avg_quality_score=sum(qualities) / len(qualities) if qualities else 0.0,
        avg_sentiment_score=sum(sentiments) / len(sentiments) if sentiments else 0.0,
        top_emotions=dict(emotion_counts.most_common(5)),
        top_intents={},
    )


@router.get("/operator/{operator_id}", response_model=OperatorReport)
async def operator_report(
    operator_id: uuid.UUID,
    period_start: date = Query(default_factory=lambda: date.today() - timedelta(days=30)),
    period_end: date = Query(default_factory=date.today),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor),
):
    op_q = await db.execute(select(User).where(User.id == operator_id, User.company_id == current_user.company_id))
    operator = op_q.scalar_one_or_none()
    if not operator:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Operator not found")

    calls_q = await db.execute(
        select(Call).where(
            Call.operator_id == operator_id,
            Call.status == CallStatus.completed,
            Call.started_at >= period_start.isoformat(),
            Call.started_at <= period_end.isoformat(),
        )
    )
    calls = calls_q.scalars().all()
    qualities = [c.quality_score for c in calls if c.quality_score is not None]
    sentiments = [c.overall_sentiment_score for c in calls if c.overall_sentiment_score is not None]
    durations = [c.duration_seconds for c in calls if c.duration_seconds is not None]

    return OperatorReport(
        operator_id=operator.id,
        operator_name=operator.full_name,
        period_start=period_start,
        period_end=period_end,
        total_calls=len(calls),
        avg_quality_score=sum(qualities) / len(qualities) if qualities else 0.0,
        avg_sentiment_score=sum(sentiments) / len(sentiments) if sentiments else 0.0,
        coaching_adherence=0.0,
    )


@router.get("/export")
async def export_report(
    format: str = Query("csv", regex="^(csv|excel)$"),
    report_date: date = Query(default_factory=date.today),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor),
):
    """Export daily report as CSV or Excel."""
    if format == "csv":
        content = "date,total_calls,avg_quality,avg_sentiment\n"
        content += f"{report_date},0,0.0,0.0\n"
        return StreamingResponse(
            io.BytesIO(content.encode("utf-8-sig")),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=report_{report_date}.csv"},
        )
    # Excel stub
    return {"message": "Excel export not yet implemented"}
