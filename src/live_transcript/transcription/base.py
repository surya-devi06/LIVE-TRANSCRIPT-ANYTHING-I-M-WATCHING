"""Abstract base classes and dataclasses for speech-recognition providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
import numpy as np


@dataclass
class TranscriptionResult:
    """Represents the recognized speech for a given audio segment."""
    text: str
    start_time: float
    end_time: float
    detected_language: Optional[str] = None
    confidence: Optional[float] = None


class SpeechRecognitionProvider(ABC):
    """Abstract interface for speech-recognition engines (Local Whisper, Cloud streaming, etc.)."""

    @abstractmethod
    def load_model(self) -> None:
        """Load recognition model into memory or initialize provider connection."""
        pass

    @abstractmethod
    def is_loaded(self) -> bool:
        """Return True if model is ready for inference."""
        pass

    @abstractmethod
    def transcribe(
        self,
        audio: np.ndarray,
        language: Optional[str] = None,
    ) -> List[TranscriptionResult]:
        """Transcribe a 16kHz mono float32 audio array into text segments.

        Parameters:
            audio: 1D numpy array of 16kHz float32 audio samples.
            language: Optional language code (e.g. 'en', 'ta', 'hi', or None/'auto').

        Returns:
            List of TranscriptionResult objects.
        """
        pass

    @abstractmethod
    def get_model_info(self) -> dict:
        """Return metadata about current model, device, and compute type."""
        pass
