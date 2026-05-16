import uuid
import hashlib
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.base import get_db
from app.models.call import Call, CallStatus
from app.models.user import User
from app.schemas.call import CallStartRequest, CallStartResponse, CallEndRequest, CallSummary, CallDetail
from app.api.deps import get_current_user
from app.core.config import get_settings

router = APIRouter(prefix="/calls", tags=["Calls"])
settings = get_settings()


@router.post("/start", response_model=CallStartResponse, status_code=status.HTTP_201_CREATED)
async def start_call(
    payload: CallStartRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    phone_hash = None
    if payload.phone_number:
        phone_hash = hashlib.sha256(payload.phone_number.encode()).hexdigest()

    call = Call(
        company_id=current_user.company_id,
        operator_id=current_user.id,
        phone_number_hash=phone_hash,
        is_autonomous=payload.is_autonomous,
    )
    db.add(call)
    await db.commit()
    await db.refresh(call)

    return CallStartResponse(
        call_id=call.id,
        websocket_url=f"/ws/call/{call.id}",
        coaching_websocket_url=f"/ws/coaching/{call.id}",
        started_at=call.started_at,
    )


@router.post("/end")
async def end_call(
    payload: CallEndRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Call).where(Call.id == payload.call_id, Call.operator_id == current_user.id))
    call = result.scalar_one_or_none()
    if not call:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call not found")

    call.ended_at = datetime.now(timezone.utc)
    call.status = CallStatus.completed
    call.duration_seconds = int((call.ended_at - call.started_at).total_seconds())
    await db.commit()
    return {"call_id": str(call.id), "duration_seconds": call.duration_seconds}


@router.get("/history", response_model=list[CallSummary])
async def call_history(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Call)
        .where(Call.company_id == current_user.company_id)
        .order_by(desc(Call.started_at))
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


@router.get("/{call_id}", response_model=CallDetail)
async def get_call(
    call_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Call)
        .options(
            selectinload(Call.transcripts),
            selectinload(Call.emotions),
            selectinload(Call.coaching_events),
        )
        .where(Call.id == call_id, Call.company_id == current_user.company_id)
    )
    call = result.scalar_one_or_none()
    if not call:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call not found")

    return CallDetail(
        id=call.id,
        status=call.status,
        started_at=call.started_at,
        ended_at=call.ended_at,
        duration_seconds=call.duration_seconds,
        overall_sentiment_score=call.overall_sentiment_score,
        quality_score=call.quality_score,
        operator_id=call.operator_id,
        transcripts=[{"text": t.text_masked or t.text, "speaker": t.speaker, "timestamp": t.timestamp} for t in call.transcripts],
        emotions=[{"emotion": e.emotion, "confidence": e.confidence, "timestamp": e.timestamp} for e in call.emotions],
        coaching_events=[{"type": c.coaching_type, "message": c.message, "timestamp": c.timestamp} for c in call.coaching_events],
    )
