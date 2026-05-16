"""
WebSocket handler for live call analysis stream.
Receives audio chunks from client, runs STT + emotion, broadcasts results.
"""
import asyncio
import base64
import time
import uuid
import numpy as np
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.websocket.connection_manager import call_manager, coaching_manager
from app.services.audio.stt_service import STTService, TranscriptResult
from app.services.audio.audio_analyzer import AudioAnalyzer, AcousticFeatures
from app.services.audio.audio_capture import AudioChunk
from app.services.nlp.emotion_service import EmotionService
from app.services.coaching.coaching_engine import CoachingEngine
from app.core.security import mask_pii
from app.core.config import get_settings

log = structlog.get_logger()
settings = get_settings()


class CallWebSocketHandler:
    """
    Protocol (JSON over WebSocket):

    Client -> Server:
      { "type": "audio_chunk", "data": "<base64 PCM float32>", "sample_rate": 16000 }
      { "type": "ping" }
      { "type": "end" }

    Server -> Client:
      { "type": "transcript", "text": "...", "masked": "...", "confidence": 0.9, "chunk_index": 0 }
      { "type": "emotion", "emotion": "neutral", "confidence": 0.8, "valence": 0.1, "arousal": 0.3 }
      { "type": "coaching", "coaching_type": "...", "message": "...", "suggested_phrase": "..." }
      { "type": "error", "detail": "..." }
      { "type": "pong" }
    """

    def __init__(self):
        self.stt = STTService(buffer_chunks=1)
        self.analyzer = AudioAnalyzer()
        self.emotion_svc = EmotionService()
        self.coaching_engine = CoachingEngine()

    async def handle(self, call_id: str, websocket: WebSocket, db: AsyncSession):
        await call_manager.connect(call_id, websocket)
        call_start = time.time()
        previous_coaching_types: list[str] = []

        try:
            while True:
                raw = await websocket.receive_text()
                import json
                msg = json.loads(raw)
                msg_type = msg.get("type")

                if msg_type == "ping":
                    await call_manager.send_personal(websocket, {"type": "pong"})
                    continue

                if msg_type == "end":
                    break

                if msg_type != "audio_chunk":
                    continue

                # Decode base64 PCM float32
                audio_bytes = base64.b64decode(msg["data"])
                audio_array = np.frombuffer(audio_bytes, dtype=np.float32)
                sample_rate = msg.get("sample_rate", settings.audio_sample_rate)

                chunk = AudioChunk(
                    data=audio_array,
                    sample_rate=sample_rate,
                    chunk_index=msg.get("chunk_index", 0),
                    timestamp=time.time(),
                )

                # Run STT
                transcript_result = await self.stt.transcribe_chunk(chunk)
                if not transcript_result or not transcript_result.text:
                    continue

                text = transcript_result.text
                masked_text = mask_pii(text)

                # Broadcast transcript
                await call_manager.broadcast(call_id, {
                    "type": "transcript",
                    "text": text,
                    "masked": masked_text,
                    "confidence": transcript_result.confidence,
                    "chunk_index": transcript_result.chunk_index,
                    "processing_ms": transcript_result.processing_time_ms,
                })

                # Acoustic features
                word_count = len(text.split())
                acoustic = await self.analyzer.extract_features(chunk, word_count)

                # Emotion analysis
                emotion_result = await self.emotion_svc.analyze(text, acoustic)
                await call_manager.broadcast(call_id, {
                    "type": "emotion",
                    "emotion": emotion_result.emotion,
                    "confidence": emotion_result.confidence,
                    "valence": emotion_result.valence,
                    "arousal": emotion_result.arousal,
                    "pitch_hz": acoustic.pitch_hz,
                    "energy_db": acoustic.energy_db,
                    "speech_rate_wpm": acoustic.speech_rate_wpm,
                })

                # Intent detection
                intent = await self.emotion_svc.detect_intent(text)

                # Coaching suggestions
                duration = int(time.time() - call_start)
                suggestions = await self.coaching_engine.generate_suggestions(
                    transcript=text,
                    emotion=emotion_result,
                    acoustic=acoustic,
                    intent=intent,
                    call_duration_seconds=duration,
                    previous_suggestions=previous_coaching_types,
                )
                for suggestion in suggestions:
                    previous_coaching_types.append(suggestion.coaching_type)
                    await coaching_manager.broadcast(call_id, {
                        "type": "coaching",
                        "coaching_type": suggestion.coaching_type,
                        "message": suggestion.message,
                        "suggested_phrase": suggestion.suggested_phrase,
                        "urgency": suggestion.urgency,
                    })

        except WebSocketDisconnect:
            log.info("ws_call_disconnected", call_id=call_id)
        except Exception as e:
            log.error("ws_call_error", call_id=call_id, error=str(e))
            try:
                await call_manager.send_personal(websocket, {"type": "error", "detail": str(e)})
            except Exception:
                pass
        finally:
            await call_manager.disconnect(call_id, websocket)
