import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.nlp.emotion_service import EmotionService
from app.services.audio.audio_analyzer import AcousticFeatures


@pytest.fixture
def emotion_svc():
    return EmotionService()


@pytest.mark.asyncio
async def test_emotion_negative(emotion_svc):
    mock_pipeline = AsyncMock(return_value=[{"label": "negative", "score": 0.92}])
    with patch("app.services.nlp.emotion_service.get_sentiment_pipeline", return_value=mock_pipeline):
        result = await emotion_svc.analyze("Bu ürün çok berbat, hiç beğenmedim")
    assert result.emotion in ("angry", "stressed", "sad", "neutral")
    assert result.nlp_label == "negative"
    assert 0 <= result.confidence <= 1


@pytest.mark.asyncio
async def test_emotion_positive(emotion_svc):
    mock_pipeline = AsyncMock(return_value=[{"label": "positive", "score": 0.88}])
    with patch("app.services.nlp.emotion_service.get_sentiment_pipeline", return_value=mock_pipeline):
        result = await emotion_svc.analyze("Çok memnun kaldım, teşekkürler!")
    assert result.nlp_label == "positive"
    assert result.valence > 0


@pytest.mark.asyncio
async def test_acoustic_fusion_angry(emotion_svc):
    acoustic = AcousticFeatures(
        pitch_hz=280.0, energy_db=-15.0,
        speech_rate_wpm=190.0, silence_ratio=0.1, zero_crossing_rate=0.05
    )
    mock_pipeline = AsyncMock(return_value=[{"label": "negative", "score": 0.85}])
    with patch("app.services.nlp.emotion_service.get_sentiment_pipeline", return_value=mock_pipeline):
        result = await emotion_svc.analyze("Çok kötü", acoustic)
    assert result.emotion == "angry"
    assert result.arousal > 0.8


@pytest.mark.asyncio
async def test_intent_complaint(emotion_svc):
    intent = await emotion_svc.detect_intent("Ürünümde sorun var, şikayet etmek istiyorum")
    assert intent["intent"] == "complaint"
    assert intent["confidence"] >= 0.7


@pytest.mark.asyncio
async def test_intent_purchase(emotion_svc):
    intent = await emotion_svc.detect_intent("Bu ürünün fiyatı nedir, satın almak istiyorum")
    assert intent["intent"] == "purchase"


@pytest.mark.asyncio
async def test_intent_info(emotion_svc):
    intent = await emotion_svc.detect_intent("Bu ürün nasıl çalışır, bilgi almak istiyorum")
    assert intent["intent"] == "info_request"
