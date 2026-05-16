"""
Real-time audio capture from microphone or phone line.
Streams PCM chunks to a queue for STT processing.
"""
import asyncio
import threading
import queue
import numpy as np
from dataclasses import dataclass
from typing import AsyncIterator
from app.core.config import get_settings

settings = get_settings()


@dataclass
class AudioChunk:
    data: np.ndarray
    sample_rate: int
    chunk_index: int
    timestamp: float


class AudioCapture:
    """
    Captures audio from input device in a background thread
    and exposes an async iterator of AudioChunk objects.
    """

    def __init__(
        self,
        sample_rate: int | None = None,
        channels: int | None = None,
        chunk_seconds: float | None = None,
    ):
        self.sample_rate = sample_rate or settings.audio_sample_rate
        self.channels = channels or settings.audio_channels
        self.chunk_seconds = chunk_seconds or settings.audio_chunk_seconds
        self.chunk_frames = int(self.sample_rate * self.chunk_seconds)
        self._queue: queue.Queue[AudioChunk | None] = queue.Queue(maxsize=20)
        self._stream = None
        self._thread: threading.Thread | None = None
        self._running = False
        self._chunk_index = 0

    def _pyaudio_callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback - runs in audio thread."""
        import pyaudio
        audio_array = np.frombuffer(in_data, dtype=np.int16).astype(np.float32) / 32768.0
        chunk = AudioChunk(
            data=audio_array,
            sample_rate=self.sample_rate,
            chunk_index=self._chunk_index,
            timestamp=time_info["input_buffer_adc_time"],
        )
        self._chunk_index += 1
        try:
            self._queue.put_nowait(chunk)
        except queue.Full:
            pass  # drop oldest - latency more important than completeness
        return (None, pyaudio.paContinue)

    def start(self, device_index: int | None = None):
        try:
            import pyaudio
            pa = pyaudio.PyAudio()
            self._pa = pa
            self._stream = pa.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_frames,
                stream_callback=self._pyaudio_callback,
            )
            self._running = True
            self._stream.start_stream()
        except ImportError:
            self._start_sounddevice(device_index)

    def _start_sounddevice(self, device_index: int | None = None):
        """Fallback to sounddevice if PyAudio not available."""
        import sounddevice as sd
        self._running = True

        def _sd_callback(indata, frames, time_info, status):
            audio_array = indata[:, 0].copy().astype(np.float32)
            import time
            chunk = AudioChunk(
                data=audio_array,
                sample_rate=self.sample_rate,
                chunk_index=self._chunk_index,
                timestamp=time.time(),
            )
            self._chunk_index += 1
            try:
                self._queue.put_nowait(chunk)
            except queue.Full:
                pass

        self._sd_stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            blocksize=self.chunk_frames,
            device=device_index,
            callback=_sd_callback,
        )
        self._sd_stream.start()

    def stop(self):
        self._running = False
        self._queue.put(None)  # sentinel
        if hasattr(self, "_stream") and self._stream:
            self._stream.stop_stream()
            self._stream.close()
        if hasattr(self, "_pa"):
            self._pa.terminate()
        if hasattr(self, "_sd_stream"):
            self._sd_stream.stop()
            self._sd_stream.close()

    async def stream_chunks(self) -> AsyncIterator[AudioChunk]:
        """Async generator yielding audio chunks."""
        loop = asyncio.get_running_loop()
        while self._running:
            chunk = await loop.run_in_executor(None, self._queue.get)
            if chunk is None:
                break
            yield chunk
