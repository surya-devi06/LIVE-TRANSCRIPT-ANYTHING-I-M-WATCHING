"""Local speech-recognition provider using Faster-Whisper with automatic CPU fallback."""

from pathlib import Path
from typing import List, Optional
import numpy as np

from live_transcript.audio.preprocessing import is_silent
from live_transcript.transcription.base import SpeechRecognitionProvider, TranscriptionResult
from live_transcript.utils.logging_setup import get_logger

logger = get_logger("transcription.local_whisper")


class LocalWhisperProvider(SpeechRecognitionProvider):
    """Local offline speech recognition using Faster-Whisper (CTranslate2)."""

    def __init__(
        self,
        model_name: str = "base",
        download_root: Optional[Path] = None,
        device: str = "auto",
        compute_type: str = "auto",
    ) -> None:
        self.model_name = model_name
        self.download_root = str(download_root) if download_root else None
        self.requested_device = device
        self.requested_compute_type = compute_type

        self.actual_device: str = "cpu"
        self.actual_compute_type: str = "int8"
        self._model = None
        self._is_loaded: bool = False

    def is_loaded(self) -> bool:
        return self._is_loaded and self._model is not None

    def load_model(self) -> None:
        """Initialize and load the Faster-Whisper model into memory with automatic GPU/CPU fallback."""
        if self._is_loaded and self._model is not None:
            return

        from faster_whisper import WhisperModel
        import ctranslate2

        logger.info(
            "Loading Faster-Whisper model '%s' (Download root: %s)...",
            self.model_name,
            self.download_root,
        )

        cuda_available = False
        try:
            cuda_available = ctranslate2.get_cuda_device_count() > 0
        except Exception:
            cuda_available = False

        # Attempt CUDA if requested and available
        if self.requested_device in ("auto", "cuda") and cuda_available:
            try:
                compute = "float16" if self.requested_compute_type == "auto" else self.requested_compute_type
                logger.info("Attempting CUDA acceleration for Whisper (%s)...", compute)
                model = WhisperModel(
                    self.model_name,
                    device="cuda",
                    compute_type=compute,
                    download_root=self.download_root,
                )
                # Verify CUDA runtime libraries by running a tiny test pass
                dummy = np.zeros(16000, dtype=np.float32)
                _ = list(model.transcribe(dummy, beam_size=1)[0])

                self._model = model
                self.actual_device = "cuda"
                self.actual_compute_type = compute
                self._is_loaded = True
                logger.info("Faster-Whisper model '%s' loaded on CUDA (%s)", self.model_name, compute)
                return
            except Exception as exc:
                logger.warning(
                    "CUDA acceleration unavailable or missing runtime libraries (%s). Falling back to CPU.",
                    exc,
                )

        # Fallback to CPU with int8 quantization for optimal performance
        cpu_compute = "int8" if self.requested_compute_type in ("auto", "int8") else "float32"
        logger.info("Loading Faster-Whisper model '%s' on CPU (%s)...", self.model_name, cpu_compute)
        self._model = WhisperModel(
            self.model_name,
            device="cpu",
            compute_type=cpu_compute,
            download_root=self.download_root,
        )
        self.actual_device = "cpu"
        self.actual_compute_type = cpu_compute
        self._is_loaded = True
        logger.info("Faster-Whisper model '%s' loaded successfully on CPU (%s)", self.model_name, cpu_compute)

    def transcribe(
        self,
        audio: np.ndarray,
        language: Optional[str] = None,
    ) -> List[TranscriptionResult]:
        """Transcribe 16kHz mono audio chunk into recognized text segments."""
        if not self.is_loaded():
            self.load_model()

        if len(audio) == 0:
            return []

        # Skip inference if audio is silent to conserve resources
        if is_silent(audio, threshold_db=-45.0):
            return []

        lang_code = None if (not language or language == "auto") else language

        try:
            segments, info = self._model.transcribe(
                audio,
                beam_size=1,
                language=lang_code,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500),
            )

            results: List[TranscriptionResult] = []
            for seg in segments:
                text = seg.text.strip()
                if text:
                    results.append(
                        TranscriptionResult(
                            text=text,
                            start_time=float(seg.start),
                            end_time=float(seg.end),
                            detected_language=info.language,
                            confidence=getattr(seg, "avg_logprob", None),
                        )
                    )

            return results
        except Exception as exc:
            logger.error("Error during Whisper inference: %s", exc)
            return []

    def get_model_info(self) -> dict:
        return {
            "model_name": self.model_name,
            "device": self.actual_device,
            "compute_type": self.actual_compute_type,
            "is_loaded": self._is_loaded,
            "download_root": self.download_root,
        }
