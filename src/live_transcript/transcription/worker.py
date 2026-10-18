"""Dedicated background transcription worker thread."""

import threading
import time
from typing import Optional
from PySide6.QtCore import QObject, Signal

from live_transcript.audio.audio_buffer import AudioChunk, BoundedAudioQueue
from live_transcript.database.models import TranscriptSegment
from live_transcript.transcription.base import SpeechRecognitionProvider
from live_transcript.utils.logging_setup import get_logger

logger = get_logger("transcription.worker")


class TranscriptionWorker(QObject):
    """Background worker that continuously pulls audio chunks and runs speech recognition."""

    # Qt Signals for UI updates
    segment_ready = Signal(object)             # (segment: TranscriptSegment)
    model_loading_started = Signal(str)        # (model_name: str)
    model_loaded = Signal(str, str)            # (model_name: str, device: str)
    status_message = Signal(str)               # (message: str)
    error_occurred = Signal(str)               # (error_message: str)
    worker_finished = Signal()

    def __init__(
        self,
        provider: SpeechRecognitionProvider,
        audio_queue: BoundedAudioQueue,
        session_id: str = "",
        source_language: str = "auto",
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)
        self.provider = provider
        self.audio_queue = audio_queue
        self.session_id = session_id
        self.source_language = source_language

        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()  # Unpaused by default

        self._sequence_number: int = 0
        self._is_running: bool = False

    @property
    def is_running(self) -> bool:
        return self._is_running

    def set_session_id(self, session_id: str) -> None:
        """Update active session ID for emitted segments."""
        self.session_id = session_id
        self._sequence_number = 0

    def start(self) -> None:
        """Start the background transcription thread."""
        if self._thread and self._thread.is_alive():
            logger.warning("TranscriptionWorker is already running.")
            return

        self._stop_event.clear()
        self._pause_event.set()
        self._is_running = True

        self._thread = threading.Thread(
            target=self._worker_loop,
            name="TranscriptionWorkerThread",
            daemon=True,
        )
        self._thread.start()
        logger.info("TranscriptionWorker thread started.")

    def pause(self) -> None:
        """Pause transcript processing."""
        self._pause_event.clear()
        logger.info("TranscriptionWorker paused.")

    def resume(self) -> None:
        """Resume transcript processing."""
        self._pause_event.set()
        logger.info("TranscriptionWorker resumed.")

    def stop(self) -> None:
        """Stop background worker thread and wait for completion."""
        if not self._thread or not self._thread.is_alive():
            self._is_running = False
            return

        logger.info("Stopping TranscriptionWorker thread...")
        self._stop_event.set()
        self._pause_event.set()  # Unpause so thread can exit wait

        self._thread.join(timeout=3.0)
        self._is_running = False
        logger.info("TranscriptionWorker thread stopped.")

    def _worker_loop(self) -> None:
        """Continuous loop consuming audio chunks from queue and running inference."""
        try:
            # 1. Load model if not loaded yet
            if not self.provider.is_loaded():
                info = self.provider.get_model_info()
                model_name = info.get("model_name", "model")
                self.model_loading_started.emit(model_name)
                self.status_message.emit(f"Loading speech recognition model ({model_name})...")

                self.provider.load_model()
                info = self.provider.get_model_info()
                device = info.get("device", "cpu")
                self.model_loaded.emit(model_name, device)
                self.status_message.emit(f"Model ready on {device.upper()}. Listening for speech...")

            # 2. Main processing loop
            while not self._stop_event.is_set():
                # While paused, do not consume from queue; wait until resumed or stopped
                while not self._pause_event.is_set() and not self._stop_event.is_set():
                    time.sleep(0.05)

                if self._stop_event.is_set():
                    break

                # Wait up to 250ms for next audio chunk from bounded queue
                chunk = self.audio_queue.get(timeout=0.25)
                if chunk is None:
                    continue

                # If paused while waiting on the queue, hold the chunk until resumed
                while not self._pause_event.is_set() and not self._stop_event.is_set():
                    time.sleep(0.05)

                if self._stop_event.is_set():
                    break

                # Run inference
                results = self.provider.transcribe(chunk.data, language=self.source_language)
                for res in results:
                    self._sequence_number += 1
                    # Absolute session timestamps
                    seg_start = chunk.start_time + res.start_time
                    seg_end = chunk.start_time + res.end_time

                    segment = TranscriptSegment.create_new(
                        session_id=self.session_id,
                        sequence_number=self._sequence_number,
                        start_time=seg_start,
                        end_time=seg_end,
                        original_text=res.text,
                        detected_language=res.detected_language,
                        status="final",
                    )
                    self.segment_ready.emit(segment)

        except Exception as exc:
            err_msg = f"Transcription worker error: {exc}"
            logger.exception(err_msg)
            self.error_occurred.emit(err_msg)
        finally:
            self._is_running = False
            self.worker_finished.emit()
            logger.info("Transcription worker thread exited.")
