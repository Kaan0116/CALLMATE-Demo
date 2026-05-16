import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.base import get_db
from app.models.call import Call
from app.models.emotion import EmotionEvent
from app.models.customer_profile import CustomerProfile
from app.models.coaching import CoachingEvent
from app.schemas.analysis import EmotionSummary, PersonalityCard, RecommendationList
from app.api.deps import get_current_user
from app.models.user import User
from app.services.nlp.personality_service import PersonalityService

router = APIRouter(prefix="/analysis", tags=["Analysis"])
personality_svc = PersonalityService()


@router.get("/emotions/{call_id}", response_model=EmotionSummary)
async def get_emotions(
    call_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    call_check = await db.execute(
        select(Call).where(Call.id == call_id, Call.company_id == current_user.company_id)
    )
    if not call_check.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call not found")

    result = await db.execute(select(EmotionEvent).where(EmotionEvent.call_id == call_id))
    emotions = result.scalars().all()

    if not emotions:
        return EmotionSummary(
            call_id=call_id, dominant_emotion="neutral",
            avg_valence=0.0, avg_arousal=0.0, emotion_timeline=[]
        )

    valences = [e.valence or 0.0 for e in emotions]
    arousals = [e.arousal or 0.0 for e in emotions]
    from collections import Counter
    dominant = Counter(e.emotion for e in emotions).most_common(1)[0][0]

    timeline = [
        {"timestamp": e.timestamp, "emotion": e.emotion, "confidence": e.confidence}
        for e in emotions
    ]

    return EmotionSummary(
        call_id=call_id,
        dominant_emotion=dominant,
        avg_valence=sum(valences) / len(valences),
        avg_arousal=sum(arousals) / len(arousals),
        emotion_timeline=timeline,
    )


@router.get("/personality/{customer_id}", response_model=PersonalityCard)
async def get_personality(
    customer_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(CustomerProfile).where(CustomerProfile.id == customer_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer profile not found")

    return PersonalityCard(
        customer_id=profile.id,
        personality_type=profile.personality_type or "unknown",
        traits=profile.personality_traits or {},
        confidence=0.7,
        recommendations=["Standart yaklaşım uygulayın"],
        total_calls=profile.total_calls,
        last_call_at=profile.last_call_at,
    )


@router.get("/recommendations/{call_id}", response_model=RecommendationList)
async def get_recommendations(
    call_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CoachingEvent).where(CoachingEvent.call_id == call_id)
    )
    events = result.scalars().all()
    pending = [e for e in events if not e.was_acknowledged]

    return RecommendationList(
        call_id=call_id,
        coaching_events=[
            {"id": str(e.id), "type": e.coaching_type, "message": e.message,
             "suggested_phrase": e.suggested_phrase, "urgency": e.urgency,
             "timestamp": e.timestamp, "acknowledged": e.was_acknowledged}
            for e in events
        ],
        pending_count=len(pending),
    )
