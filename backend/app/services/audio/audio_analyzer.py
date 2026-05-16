"""
Acoustic feature extraction: pitch, energy, speech rate.
Used alongside NLP for emotion detection.
"""
import asyncio
import numpy as np
from dataclasses import dataclass
from app.services.audio.audio_capture import AudioChunk


@dataclass
class AcousticFeatures:
    pitch_hz: float | None
    energy_db: float
    speech_rate_wpm: float | None
    silence_ratio: float
    zero_crossing_rate: float


class AudioAnalyzer:

    async def extract_features(self, chunk: AudioChunk, transcript_word_count: int = 0) -> AcousticFeatures:
        return await asyncio.get_running_loop().run_in_executor(
            None, self._extract_sync, chunk, transcript_word_count
        )

    def _extract_sync(self, chunk: AudioChunk, transcript_word_count: int) -> AcousticFeatures:
        import librosa
        audio = chunk.data
        sr = chunk.sample_rate

        # RMS energy -> dBFS
        rms = float(np.sqrt(np.mean(audio ** 2)))
        energy_db = float(20 * np.log10(rms + 1e-9))

        # Fundamental frequency (pitch) via librosa pyin
        try:
            f0, voiced_flag, _ = librosa.pyin(
                audio.astype(np.float32),
                fmin=librosa.note_to_hz("C2"),
                fmax=librosa.note_to_hz("C7"),
                sr=sr,
            )
            voiced = f0[voiced_flag] if voiced_flag is not None else np.array([])
            pitch_hz = float(np.nanmean(voiced)) if len(voiced) > 0 else None
        except Exception:
            pitch_hz = None

        # Silence ratio
        frame_length = int(sr * 0.025)
        hop_length = int(sr * 0.010)
        rms_frames = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]
        silence_threshold = 0.01
        silence_ratio = float(np.mean(rms_frames < silence_threshold))

        # Zero crossing rate
        zcr = float(np.mean(librosa.feature.zero_crossing_rate(y=audio, hop_length=hop_length)))

        # Speech rate estimation (words per minute)
        speech_rate_wpm = None
        if transcript_word_count > 0:
            duration_min = len(audio) / sr / 60.0
            speech_rate_wpm = transcript_word_count / duration_min if duration_min > 0 else None

        return AcousticFeatures(
            pitch_hz=pitch_hz,
            energy_db=energy_db,
            speech_rate_wpm=speech_rate_wpm,
            silence_ratio=silence_ratio,
            zero_crossing_rate=zcr,
        )
