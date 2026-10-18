"""Audio signal preprocessing, channel conversion, polyphase resampling, and level metering."""

import math
from typing import Tuple
import numpy as np
from scipy import signal

from live_transcript.utils.logging_setup import get_logger

logger = get_logger("audio.preprocessing")


def convert_to_mono(audio: np.ndarray) -> np.ndarray:
    """Convert multi-channel audio to single-channel (mono) float32 by averaging channels.

    Parameters:
        audio: 1D or 2D numpy array of audio samples.

    Returns:
        1D float32 numpy array.
    """
    if audio.ndim == 1:
        return audio.astype(np.float32)

    if audio.ndim == 2:
        # Average across channel axis (N, channels)
        mono = np.mean(audio, axis=-1, dtype=np.float32)
        return mono

    raise ValueError(f"Unsupported audio array dimension: {audio.ndim}")


def resample_audio(audio: np.ndarray, orig_sr: int, target_sr: int = 16000) -> np.ndarray:
    """Resample audio signal using polyphase filtering with anti-aliasing.

    Parameters:
        audio: 1D float32 numpy array.
        orig_sr: Source sample rate in Hz (e.g. 44100, 48000).
        target_sr: Target sample rate in Hz (default 16000 for Whisper).

    Returns:
        Resampled 1D float32 numpy array.
    """
    if orig_sr == target_sr:
        return audio.astype(np.float32)

    if len(audio) == 0:
        return np.empty(0, dtype=np.float32)

    # Compute irreducible ratio via greatest common divisor
    gcd = math.gcd(int(orig_sr), int(target_sr))
    up = target_sr // gcd
    down = orig_sr // gcd

    resampled = signal.resample_poly(audio, up, down).astype(np.float32)
    return resampled


def calculate_rms_and_level(audio: np.ndarray) -> Tuple[float, float]:
    """Calculate root-mean-square amplitude in dBFS and a normalized 0.0 - 1.0 linear meter level.

    Returns:
        (rms_db, linear_level):
            rms_db: Float in dBFS (range -60.0 to 0.0 dB).
            linear_level: Float normalized 0.0 to 1.0 suitable for UI volume meters.
    """
    if len(audio) == 0:
        return -60.0, 0.0

    # Mean squared amplitude
    ms = np.mean(np.square(audio))
    rms = float(np.sqrt(ms)) if ms > 0 else 0.0

    if rms <= 1e-6:
        return -60.0, 0.0

    # Decibels relative to full scale (dBFS)
    db = 20.0 * math.log10(rms)
    # Clamp dB between -60 dBFS and 0 dBFS
    clamped_db = max(-60.0, min(0.0, db))

    # Normalized 0.0 - 1.0 visual level
    linear_level = (clamped_db + 60.0) / 60.0
    return clamped_db, linear_level


def is_silent(audio: np.ndarray, threshold_db: float = -50.0) -> bool:
    """Determine whether an audio chunk consists solely of silence or background noise."""
    rms_db, _ = calculate_rms_and_level(audio)
    return rms_db < threshold_db


class AudioPreprocessor:
    """Unified audio preprocessor pipeline converting any incoming audio to 16kHz mono float32."""

    def __init__(self, target_sample_rate: int = 16000) -> None:
        self.target_sample_rate = target_sample_rate

    def process(self, raw_audio: np.ndarray, source_sample_rate: int) -> np.ndarray:
        """Process raw captured audio chunk into standardized Whisper input format."""
        mono = convert_to_mono(raw_audio)
        resampled = resample_audio(mono, orig_sr=source_sample_rate, target_sr=self.target_sample_rate)
        return resampled
