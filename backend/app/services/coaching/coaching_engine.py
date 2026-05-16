"""
Live coaching engine - generates real-time suggestions for operators.
Runs after each transcript chunk + emotion analysis.
"""
from dataclasses import dataclass
from app.services.nlp.emotion_service import EmotionResult
from app.services.audio.audio_analyzer import AcousticFeatures


@dataclass
class CoachingSuggestion:
    coaching_type: str
    message: str
    suggested_phrase: str | None
    urgency: str  # low, normal, high


class CoachingEngine:
    """
    Rule-based + ML-assisted coaching suggestion generator.
    Produces zero or more suggestions per transcript+emotion chunk.
    """

    # Turkish script templates
    _SCRIPTS = {
        "empathy_complaint": "Anlıyorum, bu durum gerçekten can sıkıcı olmuş. Hemen çözüm üretiyorum.",
        "calm_angry": "Sakin olun lütfen, sorununuzu en kısa sürede çözeceğim.",
        "sales_offer": "Size özel bir kampanyamız var, uygun mudur?",
        "close_sale": "Hemen işlemi başlatalım mı?",
        "clarify": "Sizi doğru anladığımdan emin olmak için tekrar eder misiniz?",
        "thank_you": "İlginiz için teşekkür ederim, başka yardımcı olabileceğim bir konu var mı?",
    }

    async def generate_suggestions(
        self,
        transcript: str,
        emotion: EmotionResult,
        acoustic: AcousticFeatures | None,
        intent: dict,
        call_duration_seconds: int,
        previous_suggestions: list[str],
    ) -> list[CoachingSuggestion]:
        suggestions: list[CoachingSuggestion] = []

        # Tone warnings
        if acoustic:
            if acoustic.pitch_hz and acoustic.pitch_hz > 260:
                suggestions.append(CoachingSuggestion(
                    coaching_type="tone_warning",
                    message="Sesiniz çok yüksek tonda, lütfen daha sakin konuşun.",
                    suggested_phrase=None,
                    urgency="high",
                ))
            if acoustic.speech_rate_wpm and acoustic.speech_rate_wpm > 180:
                suggestions.append(CoachingSuggestion(
                    coaching_type="tone_warning",
                    message="Konuşma hızınız çok yüksek, daha yavaş konuşun.",
                    suggested_phrase=None,
                    urgency="normal",
                ))

        # Emotion-based coaching
        if emotion.emotion == "angry" and "calm_angry" not in previous_suggestions:
            suggestions.append(CoachingSuggestion(
                coaching_type="script_suggestion",
                message="Müşteri öfkeli görünüyor. Sakinleştirici bir yaklaşım deneyin.",
                suggested_phrase=self._SCRIPTS["calm_angry"],
                urgency="high",
            ))

        if emotion.emotion in ("sad", "stressed") and "empathy_complaint" not in previous_suggestions:
            suggestions.append(CoachingSuggestion(
                coaching_type="script_suggestion",
                message="Müşteri stresli/üzgün. Empati gösterin.",
                suggested_phrase=self._SCRIPTS["empathy_complaint"],
                urgency="normal",
            ))

        # Intent-based
        if intent.get("intent") == "purchase" and "sales_offer" not in previous_suggestions:
            suggestions.append(CoachingSuggestion(
                coaching_type="sales_opportunity",
                message="Satın alma niyeti tespit edildi! Kampanya sunun.",
                suggested_phrase=self._SCRIPTS["sales_offer"],
                urgency="high",
            ))

        if intent.get("intent") == "complaint":
            suggestions.append(CoachingSuggestion(
                coaching_type="procedure_step",
                message="Şikayet prosedürü: 1) Özür dile 2) Çözüm sun 3) Takip et",
                suggested_phrase=self._SCRIPTS["empathy_complaint"],
                urgency="normal",
            ))

        # Long call warning
        if call_duration_seconds > 600 and "close_sale" not in previous_suggestions:
            suggestions.append(CoachingSuggestion(
                coaching_type="procedure_step",
                message="Görüşme 10 dakikayı geçti. Sonuçlandırmayı düşünün.",
                suggested_phrase=self._SCRIPTS["close_sale"],
                urgency="low",
            ))

        return suggestions
