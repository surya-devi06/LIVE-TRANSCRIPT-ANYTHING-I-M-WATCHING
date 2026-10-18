"""Unit tests for audio preprocessing: mono conversion, resampling, RMS and silence detection."""

import numpy as np
import pytest

from live_transcript.audio.preprocessing import (
    AudioPreprocessor,
    calculate_rms_and_level,
    convert_to_mono,
    is_silent,
    resample_audio,
)


def test_convert_to_mono_1d() -> None:
    """1D audio array should return unchanged as float32."""
    mono_in = np.array([0.1, -0.2, 0.3], dtype=np.float32)
    mono_out = convert_to_mono(mono_in)
    assert mono_out.shape == (3,)
    assert mono_out.dtype == np.float32
    np.testing.assert_allclose(mono_in, mono_out)


def test_convert_to_mono_stereo() -> None:
    """Stereo (2 channels) should be averaged across channels."""
    stereo = np.array(
        [[0.2, 0.4], [-0.1, -0.3], [0.6, 0.0]],
        dtype=np.float32,
    )
    mono = convert_to_mono(stereo)
    assert mono.shape == (3,)
    assert mono.dtype == np.float32
    expected = np.array([0.3, -0.2, 0.3], dtype=np.float32)
    np.testing.assert_allclose(mono, expected, rtol=1e-5)


def test_resample_audio_48k_to_16k() -> None:
    """Resampling 1 second of 48000 Hz audio should yield exactly 16000 samples."""
    # 48000 samples of a 440 Hz sine wave
    duration = 1.0
    t = np.linspace(0, duration, int(48000 * duration), endpoint=False)
    sine_48k = np.sin(2 * np.pi * 440 * t).astype(np.float32)

    resampled = resample_audio(sine_48k, orig_sr=48000, target_sr=16000)
    assert len(resampled) == 16000
    assert resampled.dtype == np.float32


def test_resample_audio_same_rate() -> None:
    """Resampling with identical source and target rate returns float32 copy."""
    audio = np.array([0.5, -0.5, 0.2], dtype=np.float32)
    resampled = resample_audio(audio, orig_sr=16000, target_sr=16000)
    np.testing.assert_allclose(audio, resampled)


def test_calculate_rms_and_level_silence() -> None:
    """Zero audio should yield minimal dBFS (-60 dB) and 0.0 linear level."""
    silence = np.zeros(1000, dtype=np.float32)
    db, linear = calculate_rms_and_level(silence)
    assert db <= -59.0
    assert linear == 0.0


def test_calculate_rms_and_level_full_scale() -> None:
    """Unit sine wave should yield approx -3 dBFS and linear level near ~0.95."""
    t = np.linspace(0, 1, 16000, endpoint=False)
    sine = np.sin(2 * np.pi * 1000 * t).astype(np.float32)
    db, linear = calculate_rms_and_level(sine)
    assert -4.0 <= db <= -2.0
    assert 0.85 <= linear <= 1.0


def test_is_silent() -> None:
    """Silence threshold verification."""
    silence = np.zeros(1600, dtype=np.float32)
    assert is_silent(silence, threshold_db=-50.0) is True

    audible = np.full(1600, 0.5, dtype=np.float32)
    assert is_silent(audible, threshold_db=-50.0) is False


def test_audio_preprocessor_pipeline() -> None:
    """Full pipeline test converting 48kHz stereo to 16kHz mono."""
    stereo_48k = np.ones((4800, 2), dtype=np.float32) * 0.5
    preprocessor = AudioPreprocessor(target_sample_rate=16000)
    out = preprocessor.process(stereo_48k, source_sample_rate=48000)

    assert out.ndim == 1
    assert len(out) == 1600
    assert out.dtype == np.float32
