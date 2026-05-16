"""
Dynamic customer personality profiling using call history embeddings.
Stores and retrieves personality vectors from Qdrant.
"""
import uuid
import asyncio
import hashlib
from dataclasses import dataclass
import structlog
from app.core.config import get_settings

log = structlog.get_logger()
settings = get_settings()

_qdrant_client = None
_embedder = None
_qdrant_lock = asyncio.Lock()


async def get_qdrant():
    global _qdrant_client
    async with _qdrant_lock:
        if _qdrant_client is None:
            from qdrant_client import AsyncQdrantClient
            from qdrant_client.models import VectorParams, Distance
            _qdrant_client = AsyncQdrantClient(
                host=settings.qdrant_host, port=settings.qdrant_port
            )
            try:
                await _qdrant_client.create_collection(
                    collection_name=settings.qdrant_collection,
                    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
                )
                log.info("qdrant_collection_created", name=settings.qdrant_collection)
            except Exception:
                pass  # collection already exists
    return _qdrant_client


async def get_embedder():
    global _embedder
    if _embedder is None:
        from transformers import AutoTokenizer, AutoModel
        import torch

        tokenizer = await asyncio.get_running_loop().run_in_executor(
            None, AutoTokenizer.from_pretrained, settings.nlp_model
        )
        model = await asyncio.get_running_loop().run_in_executor(
            None, AutoModel.from_pretrained, settings.nlp_model
        )
        _embedder = (tokenizer, model)
    return _embedder


@dataclass
class PersonalityProfile:
    personality_type: str
    traits: dict
    confidence: float
    recommendations: list[str]


_PERSONALITY_RULES = {
    "impatient": {
        "signals": ["çabuk", "hızlı", "beklemek", "uzun süre"],
        "traits": {"patience": 0.2, "directness": 0.9},
        "recommendations": ["Kısa ve net yanıtlar verin", "Bekleme sürelerini minimize edin"],
    },
    "analytical": {
        "signals": ["neden", "nasıl", "detay", "açıkla", "sebep"],
        "traits": {"patience": 0.8, "detail_orientation": 0.95},
        "recommendations": ["Detaylı açıklamalar yapın", "Veri ve kanıtlar sunun"],
    },
    "emotional": {
        "signals": ["üzüldüm", "mutlu", "hayal kırıklığı", "memnunum"],
        "traits": {"emotionality": 0.9, "empathy_need": 0.85},
        "recommendations": ["Empati gösterin", "Duygusal onay verin"],
    },
    "decisive": {
        "signals": ["tamam", "anlaştık", "evet", "hayır", "kesin"],
        "traits": {"decisiveness": 0.9, "patience": 0.6},
        "recommendations": ["Hızlı karar noktaları sunun", "Alternatifleri sınırlı tutun"],
    },
}


class PersonalityService:

    async def embed_text(self, text: str) -> list[float]:
        tokenizer, model = await get_embedder()
        import torch

        def _encode():
            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
            with torch.no_grad():
                outputs = model(**inputs)
            return outputs.last_hidden_state[:, 0, :].squeeze().tolist()

        return await asyncio.get_running_loop().run_in_executor(None, _encode)

    async def analyze_personality(self, transcript_history: list[str]) -> PersonalityProfile:
        combined_text = " ".join(transcript_history[-20:])  # last 20 utterances
        text_lower = combined_text.lower()

        scores: dict[str, float] = {}
        for ptype, config in _PERSONALITY_RULES.items():
            matches = sum(1 for signal in config["signals"] if signal in text_lower)
            scores[ptype] = matches / len(config["signals"])

        if not scores or max(scores.values()) == 0:
            return PersonalityProfile(
                personality_type="neutral",
                traits={"patience": 0.5, "directness": 0.5},
                confidence=0.3,
                recommendations=["Standart iletişim yaklaşımı uygulayın"],
            )

        top_type = max(scores, key=scores.get)
        config = _PERSONALITY_RULES[top_type]
        confidence = min(scores[top_type] * 2, 1.0)

        return PersonalityProfile(
            personality_type=top_type,
            traits=config["traits"],
            confidence=confidence,
            recommendations=config["recommendations"],
        )

    async def upsert_profile(self, phone_hash: str, transcript_history: list[str]) -> str:
        """Store customer embedding in Qdrant. Returns point ID."""
        client = await get_qdrant()
        combined = " ".join(transcript_history[-30:])
        embedding = await self.embed_text(combined)

        from qdrant_client.models import PointStruct
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, phone_hash))
        await client.upsert(
            collection_name=settings.qdrant_collection,
            points=[PointStruct(
                id=point_id,
                vector=embedding,
                payload={"phone_hash": phone_hash},
            )],
        )
        return point_id

    async def find_similar_customers(self, embedding: list[float], limit: int = 5) -> list[dict]:
        client = await get_qdrant()
        results = await client.search(
            collection_name=settings.qdrant_collection,
            query_vector=embedding,
            limit=limit,
        )
        return [{"id": r.id, "score": r.score, "payload": r.payload} for r in results]
