"""Unit tests for LocalWhisperProvider and SpeechRecognitionProvider interface."""

from pathlib import Path
import numpy as np
import pytest

from live_transcript.transcription.base import SpeechRecognitionProvider, TranscriptionResult
from live_transcript.transcription.local_whisper import LocalWhisperProvider


class DummySpeechProvider(SpeechRecognitionProvider):
    """Mock speech provider for deterministic unit testing."""

    def __init__(self) -> None:
        self._loaded = False

    def load_model(self) -> None:
        self._loaded = True

    def is_loaded(self) -> bool:
        return self._loaded

    def transcribe(self, audio: np.ndarray, language=None) -> list[TranscriptionResult]:
        if len(audio) == 0:
            return []
        return [
            TranscriptionResult(
                text="Hello world from speech recognition",
                start_time=0.0,
                end_time=2.5,
                detected_language="en",
                confidence=0.95,
            )
        ]

    def get_model_info(self) -> dict:
        return {
            "model_name": "dummy",
            "device": "cpu",
            "compute_type": "float32",
            "is_loaded": self._loaded,
            "download_root": None,
        }


def test_dummy_speech_provider() -> None:
    """Verify SpeechRecognitionProvider interface contract."""
    provider = DummySpeechProvider()
    assert provider.is_loaded() is False
    provider.load_model()
    assert provider.is_loaded() is True

    audio = np.ones(16000, dtype=np.float32)
    results = provider.transcribe(audio)
    assert len(results) == 1
    assert results[0].text == "Hello world from speech recognition"
    assert results[0].detected_language == "en"


def test_local_whisper_provider_metadata(temp_data_dir: Path) -> None:
    """Verify LocalWhisperProvider initializes correctly and reports metadata."""
    provider = LocalWhisperProvider(
        model_name="tiny",
        download_root=temp_data_dir / "models",
        device="cpu",
        compute_type="int8",
    )
    assert provider.is_loaded() is False

    info = provider.get_model_info()
    assert info["model_name"] == "tiny"
    assert info["is_loaded"] is False


def test_local_whisper_provider_silence_skip(temp_data_dir: Path) -> None:
    """Verify silence is detected and skipped without calling inference."""
    provider = LocalWhisperProvider(
        model_name="tiny",
        download_root=temp_data_dir / "models",
        device="cpu",
        compute_type="int8",
    )
    # Silent audio array
    silence = np.zeros(16000, dtype=np.float32)
    # Even if model is not loaded yet, silence should return empty without error
    results = provider.transcribe(silence)
    assert results == []
