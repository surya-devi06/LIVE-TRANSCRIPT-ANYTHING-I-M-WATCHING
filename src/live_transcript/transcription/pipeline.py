"""End-to-end transcription pipeline coordinating audio capture, worker, and database persistence."""

import time
from typing import Optional
from PySide6.QtCore import QObject, Signal

from live_transcript.audio.capture import AudioCaptureService
from live_transcript.config import AppConfig
from live_transcript.constants import AppState, AudioSourceType
from live_transcript.database.models import Session, TranscriptSegment, utc_now_iso
from live_transcript.database.repositories import SegmentRepository, SessionRepository
from live_transcript.transcription.base import SpeechRecognitionProvider
from live_transcript.transcription.local_whisper import LocalWhisperProvider
from live_transcript.transcription.worker import TranscriptionWorker
from live_transcript.utils.logging_setup import get_logger

logger = get_logger("transcription.pipeline")


class TranscriptionPipeline(QObject):
    """Coordinates audio capture, speech recognition, and persistent storage."""

    # UI Signals
    session_started = Signal(object)      # (session: Session)
    session_ended = Signal(object)        # (session: Session)
    segment_received = Signal(object)     # (segment: TranscriptSegment)
    level_meter_updated = Signal(float, float) # (linear: 0-1, db: -60-0)
    pipeline_state_changed = Signal(object, str) # (state: AppState, message: str)
    status_message = Signal(str)
    error_occurred = Signal(str)

    def __init__(
        self,
        config: AppConfig,
        session_repo: SessionRepository,
        segment_repo: SegmentRepository,
        audio_service: AudioCaptureService,
        speech_provider: Optional[SpeechRecognitionProvider] = None,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)
        self.config = config
        self.session_repo = session_repo
        self.segment_repo = segment_repo
        self.audio_service = audio_service

        self.speech_provider = speech_provider or LocalWhisperProvider(
            model_name=self.config.model_name,
            download_root=self.config.models_dir,
        )

        self.worker = TranscriptionWorker(
            provider=self.speech_provider,
            audio_queue=self.audio_service.audio_queue,
            source_language=self.config.source_language,
            parent=self,
        )

        self.current_session: Optional[Session] = None
        self._session_start_time: float = 0.0
        self._is_running: bool = False
        self._is_paused: bool = False

        self._wire_signals()

    def _wire_signals(self) -> None:
        # Audio service signals
        self.audio_service.level_meter_updated.connect(self.level_meter_updated)
        self.audio_service.error_occurred.connect(self.error_occurred)

        # Worker signals
        self.worker.segment_ready.connect(self._on_segment_ready)
        self.worker.status_message.connect(self.status_message)
        self.worker.error_occurred.connect(self.error_occurred)
        self.worker.model_loaded.connect(self._on_model_loaded)

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    def start_session(
        self,
        title: Optional[str] = None,
        source_type: AudioSourceType = AudioSourceType.SYSTEM_LOOPBACK,
        device_id: Optional[str] = None,
    ) -> Session:
        """Start a new audio capture and transcription session."""
        if self._is_running:
            logger.warning("Pipeline is already running.")
            return self.current_session

        session_title = title or f"Live Session ({time.strftime('%Y-%m-%d %H:%M')})"
        provider_info = self.speech_provider.get_model_info()

        # 1. Create and persist new session in SQLite
        session = Session.create_new(
            title=session_title,
            source_type=source_type.value,
            source_language=self.config.source_language,
            target_language=self.config.target_language,
            transcription_provider="faster-whisper",
            model_name=self.config.model_name,
        )
        self.session_repo.create(session)
        self.current_session = session
        self._session_start_time = time.time()
        self._is_running = True
        self._is_paused = False

        logger.info("Created new session in SQLite (ID: %s, Title: '%s')", session.id, session.title)

        # 2. Configure and start audio capture & worker
        self.audio_service.set_source(source_type, device_id=device_id)
        self.worker.set_session_id(session.id)
        self.worker.source_language = self.config.source_language

        self.audio_service.start()
        self.worker.start()

        self.pipeline_state_changed.emit(AppState.TRANSCRIBING, "Listening and transcribing...")
        self.session_started.emit(session)
        return session

    def pause(self) -> None:
        """Pause capture and transcription."""
        if self._is_running and not self._is_paused:
            self._is_paused = True
            self.audio_service.pause()
            self.worker.pause()
            self.pipeline_state_changed.emit(AppState.PAUSED, "Transcription paused.")
            logger.info("Pipeline paused.")

    def resume(self) -> None:
        """Resume capture and transcription."""
        if self._is_running and self._is_paused:
            self._is_paused = False
            self.audio_service.resume()
            self.worker.resume()
            self.pipeline_state_changed.emit(AppState.TRANSCRIBING, "Transcription resumed.")
            logger.info("Pipeline resumed.")

    def stop_session(self) -> Optional[Session]:
        """Stop capture, finalize pending transcript segments, and persist session metadata."""
        if not self._is_running:
            return self.current_session

        logger.info("Stopping transcription pipeline...")
        # Stop capture first so remaining audio is flushed to queue
        self.audio_service.stop()
        # Stop worker
        self.worker.stop()

        session = self.current_session
        if session:
            session.ended_at = utc_now_iso()
            session.duration_seconds = max(0.0, time.time() - self._session_start_time)
            self.session_repo.update(session)
            logger.info(
                "Finalized session '%s' (Duration: %.1fs, Segments: %d)",
                session.title,
                session.duration_seconds,
                self.segment_repo.count_for_session(session.id),
            )

        self._is_running = False
        self._is_paused = False
        self.pipeline_state_changed.emit(AppState.STOPPED, "Session stopped.")
        if session:
            self.session_ended.emit(session)

        return session

    def _on_segment_ready(self, segment: TranscriptSegment) -> None:
        """Persist recognized segment to SQLite and notify listeners."""
        try:
            self.segment_repo.add(segment)
            logger.debug("Segment #%d saved: '%s'", segment.sequence_number, segment.original_text)
            self.segment_received.emit(segment)
        except Exception as exc:
            logger.error("Failed to persist transcript segment #%d: %s", segment.sequence_number, exc)

    def _on_model_loaded(self, model_name: str, device: str) -> None:
        """Handle model readiness."""
        logger.info("Model '%s' ready on %s", model_name, device.upper())
        self.pipeline_state_changed.emit(AppState.TRANSCRIBING, f"Transcribing with {model_name} ({device.upper()})")
