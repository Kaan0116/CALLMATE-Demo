import pytest
from app.services.coaching.coaching_engine import CoachingEngine
from app.services.nlp.emotion_service import EmotionResult
from app.services.audio.audio_analyzer import AcousticFeatures


@pytest.fixture
def engine():
    return CoachingEngine()


@pytest.fixture
def angry_emotion():
    return EmotionResult(
        emotion="angry", confidence=0.9, valence=-0.8,
        arousal=0.9, nlp_label="negative", nlp_score=0.9
    )


@pytest.fixture
def high_pitch_acoustic():
    return AcousticFeatures(
        pitch_hz=270.0, energy_db=-18.0,
        speech_rate_wpm=200.0, silence_ratio=0.05, zero_crossing_rate=0.06
    )


@pytest.mark.asyncio
async def test_tone_warning_high_pitch(engine, angry_emotion, high_pitch_acoustic):
    suggestions = await engine.generate_suggestions(
        transcript="Anlıyorum",
        emotion=angry_emotion,
        acoustic=high_pitch_acoustic,
        intent={"intent": "complaint"},
        call_duration_seconds=60,
        previous_suggestions=[],
    )
    types = [s.coaching_type for s in suggestions]
    assert "tone_warning" in types


@pytest.mark.asyncio
async def test_sales_opportunity(engine):
    neutral = EmotionResult(emotion="neutral", confidence=0.7, valence=0.1, arousal=0.3, nlp_label="notr", nlp_score=0.7)
    suggestions = await engine.generate_suggestions(
        transcript="Satın almak istiyorum",
        emotion=neutral,
        acoustic=None,
        intent={"intent": "purchase", "confidence": 0.9},
        call_duration_seconds=120,
        previous_suggestions=[],
    )
    types = [s.coaching_type for s in suggestions]
    assert "sales_opportunity" in types


@pytest.mark.asyncio
async def test_no_duplicate_suggestions(engine, angry_emotion):
    suggestions = await engine.generate_suggestions(
        transcript="Sinir bozucu",
        emotion=angry_emotion,
        acoustic=None,
        intent={"intent": "complaint"},
        call_duration_seconds=60,
        previous_suggestions=["script_suggestion"],
    )
    types = [s.coaching_type for s in suggestions]
    assert types.count("script_suggestion") == 0


@pytest.mark.asyncio
async def test_long_call_warning(engine):
    neutral = EmotionResult(emotion="neutral", confidence=0.7, valence=0.1, arousal=0.3, nlp_label="notr", nlp_score=0.7)
    suggestions = await engine.generate_suggestions(
        transcript="Devam edelim",
        emotion=neutral,
        acoustic=None,
        intent={"intent": "general"},
        call_duration_seconds=700,
        previous_suggestions=[],
    )
    types = [s.coaching_type for s in suggestions]
    assert "procedure_step" in types
