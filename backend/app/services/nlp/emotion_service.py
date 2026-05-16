"""
Multimodal emotion detection: combines NLP sentiment + acoustic features.
Turkish-optimized using savasy/bert-base-turkish-sentiment-cased.
"""
import asyncio
from dataclasses import dataclass
import structlog
from app.core.config import get_settings
from app.services.audio.audio_analyzer import AcousticFeatures

log = structlog.get_logger()
settings = get_settings()

_sentiment_pipeline = None
_pipeline_lock = asyncio.Lock()


async def get_sentiment_pipeline():
    global _sentiment_pipeline
    async with _pipeline_lock:
        if _sentiment_pipeline is None:
            from transformers import pipeline
            log.info("loading_sentiment_model", model=settings.sentiment_model)
            _sentiment_pipeline = await asyncio.get_running_loop().run_in_executor(
                None,
                lambda: pipeline(
                    "text-classification",
                    model=settings.sentiment_model,
                    tokenizer=settings.sentiment_model,
                    device=-1,
                    truncation=True,
                    max_length=512,
                ),
            )
            log.info("sentiment_model_loaded")
    return _sentiment_pipeline


@dataclass
class EmotionResult:
    emotion: str        # happy, angry, stressed, neutral, sad, excited
    confidence: float
    valence: float      # -1 (negative) to 1 (positive)
    arousal: float      # 0 (calm) to 1 (excited)
    nlp_label: str
    nlp_score: float


_LABEL_MAP = {
    "positive": ("happy", 0.7, 0.5),
    "negative": ("angry", -0.7, 0.7),
    "notr": ("neutral", 0.0, 0.2),
    "neutral": ("neutral", 0.0, 0.2),
}


class EmotionService:

    async def analyze(
        self,
        text: str,
        acoustic: AcousticFeatures | None = None,
    ) -> EmotionResult:
        pipeline = await get_sentiment_pipeline()
        raw = await asyncio.get_running_loop().run_in_executor(
            None, lambda: pipeline(text)[0]
        )
        nlp_label = raw["label"].lower()
        nlp_score = float(raw["score"])

        emotion, valence, arousal = _LABEL_MAP.get(nlp_label, ("neutral", 0.0, 0.2))

        if acoustic:
            emotion, valence, arousal = self._fuse_acoustic(
                emotion, valence, arousal, nlp_score, acoustic
            )

        return EmotionResult(
            emotion=emotion,
            confidence=nlp_score,
            valence=valence,
            arousal=arousal,
            nlp_label=nlp_label,
            nlp_score=nlp_score,
        )

    def _fuse_acoustic(
        self,
        emotion: str,
        valence: float,
        arousal: float,
        nlp_score: float,
        acoustic: AcousticFeatures,
    ) -> tuple[str, float, float]:
        """Rule-based acoustic fusion for emotion refinement."""
        energy = acoustic.energy_db
        pitch = acoustic.pitch_hz or 150.0
        rate = acoustic.speech_rate_wpm or 120.0

        # High energy + high pitch + fast speech -> stress / anger
        if energy > -20 and pitch > 220 and rate > 160:
            if valence < 0:
                return "angry", -0.85, 0.90
            return "stressed", -0.4, 0.85

        # Low energy + slow speech -> sad
        if energy < -40 and rate < 80 and valence < 0:
            return "sad", -0.6, 0.15

        # High energy + positive -> excited
        if energy > -25 and valence > 0.5:
            return "excited", 0.8, 0.85

        return emotion, valence, arousal

    async def detect_intent(self, text: str) -> dict:
        """Detect customer intent: complaint, purchase, info_request."""
        text_lower = text.lower()
        if any(w in text_lower for w in ["şikayet", "sorun", "problem", "olmadı", "bozuk", "hata"]):
            return {"intent": "complaint", "confidence": 0.85}
        if any(w in text_lower for w in ["satın", "almak", "sipariş", "fiyat", "ücret"]):
            return {"intent": "purchase", "confidence": 0.80}
        if any(w in text_lower for w in ["nasıl", "nedir", "bilgi", "öğrenmek", "ne zaman"]):
            return {"intent": "info_request", "confidence": 0.75}
        return {"intent": "general", "confidence": 0.60}

    async def detect_profanity(self, text: str) -> bool:
        """Simple Turkish profanity detection."""
        profanity_list = [
            "küfür1", "küfür2",  # replace with actual list in production
        ]
        text_lower = text.lower()
        return any(w in text_lower for w in profanity_list)
