"""Speech recognition and live transcription module."""

from live_transcript.transcription.base import SpeechRecognitionProvider, TranscriptionResult
from live_transcript.transcription.local_whisper import LocalWhisperProvider
from live_transcript.transcription.pipeline import TranscriptionPipeline
from live_transcript.transcription.worker import TranscriptionWorker

__all__ = [
    "SpeechRecognitionProvider",
    "TranscriptionResult",
    "LocalWhisperProvider",
    "TranscriptionWorker",
    "TranscriptionPipeline",
]
