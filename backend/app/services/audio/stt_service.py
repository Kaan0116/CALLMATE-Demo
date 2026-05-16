"""
Speech-to-Text service using faster-whisper (CTranslate2 backend).
4x faster than openai-whisper, lower memory, pre-built wheels.
"""
import asyncio
import time
import numpy as np
from dataclasses import dataclass
from typing import AsyncIterator
import structlog
from app.core.config import get_settings
from app.services.audio.audio_capture import AudioChunk

log = structlog.get_logger()
settings = get_settings()

_whisper_model = None
_model_lock = asyncio.Lock()


async def get_whisper_model():
    global _whisper_model
    async with _model_lock:
        if _whisper_model is None:
            from faster_whisper import WhisperModel
            log.info("loading_whisper", model=settings.whisper_model, device=settings.whisper_device)
            _whisper_model = await asyncio.get_running_loop().run_in_executor(
                None,
                lambda: WhisperModel(
                    settings.whisper_model,
                    device=settings.whisper_device,
                    compute_type="int8",   # CPU için optimal
                ),
            )
            log.info("whisper_loaded")
    return _whisper_model


@dataclass
class TranscriptResult:
    text: str
    language: str
    confidence: float
    chunk_index: int
    processing_time_ms: float
    no_speech_prob: float
    segments: list[dict]


class STTService:
    """
    Wraps faster-whisper inference. Buffers AudioChunks before transcribing
    to improve accuracy on short utterances.
    """

    def __init__(self, buffer_chunks: int = 1):
        self.buffer_chunks = buffer_chunks
        self._buffer: list[AudioChunk] = []

    async def transcribe_chunk(self, chunk: AudioChunk) -> TranscriptResult | None:
        self._buffer.append(chunk)
        if len(self._buffer) < self.buffer_chunks:
            return None
        return await self._run_inference()

    async def flush(self) -> TranscriptResult | None:
        if not self._buffer:
            return None
        return await self._run_inference()

    async def _run_inference(self) -> TranscriptResult:
        model = await get_whisper_model()
        audio_data = np.concatenate([c.data for c in self._buffer])
        chunk_index = self._buffer[-1].chunk_index
        self._buffer.clear()

        t0 = time.perf_counter()

        def _transcribe():
            segments_gen, info = model.transcribe(
                audio_data,
                language=settings.whisper_language,
                task="transcribe",
                beam_size=5,
                vad_filter=True,
                vad_parameters={"min_silence_duration_ms": 500},
            )
            segments = list(segments_gen)
            full_text = " ".join(s.text.strip() for s in segments)
            avg_no_speech = 1.0 - info.language_probability if segments else 1.0
            avg_logprob = float(np.mean([s.avg_logprob for s in segments])) if segments else -1.0
            confidence = float(np.exp(avg_logprob)) if segments else 0.0
            seg_dicts = [
                {
                    "start": s.start,
                    "end": s.end,
                    "text": s.text,
                    "avg_logprob": s.avg_logprob,
                    "no_speech_prob": s.no_speech_prob,
                }
                for s in segments
            ]
            return full_text, info.language, confidence, avg_no_speech, seg_dicts

        full_text, lang, confidence, no_speech_prob, seg_dicts = \
            await asyncio.get_running_loop().run_in_executor(None, _transcribe)

        elapsed_ms = (time.perf_counter() - t0) * 1000

        return TranscriptResult(
            text=full_text,
            language=lang or settings.whisper_language,
            confidence=confidence,
            chunk_index=chunk_index,
            processing_time_ms=elapsed_ms,
            no_speech_prob=no_speech_prob,
            segments=seg_dicts,
        )

    async def stream_transcripts(
        self, audio_stream: AsyncIterator[AudioChunk]
    ) -> AsyncIterator[TranscriptResult]:
        """Process a stream of AudioChunks and yield TranscriptResults."""
        async for chunk in audio_stream:
            result = await self.transcribe_chunk(chunk)
            if result and result.text and result.no_speech_prob < 0.6:
                yield result
        final = await self.flush()
        if final and final.text and final.no_speech_prob < 0.6:
            yield final
