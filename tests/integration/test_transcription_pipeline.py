"""Integration test for full TranscriptionPipeline with SQLite persistence."""

import time
import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from live_transcript.audio.audio_buffer import AudioChunk
from live_transcript.audio.capture import AudioCaptureService
from live_transcript.config import AppConfig
from live_transcript.constants import AppState, AudioSourceType
from live_transcript.database.connection import DatabaseConnection
from live_transcript.database.models import Session, TranscriptSegment
from live_transcript.database.repositories import SegmentRepository, SessionRepository
from live_transcript.transcription.base import SpeechRecognitionProvider, TranscriptionResult
from live_transcript.transcription.pipeline import TranscriptionPipeline


class PipelineMockProvider(SpeechRecognitionProvider):
    def __init__(self) -> None:
        self._loaded = True

    def load_model(self) -> None:
        self._loaded = True

    def is_loaded(self) -> bool:
        return self._loaded

    def transcribe(self, audio: np.ndarray, language=None) -> list[TranscriptionResult]:
        return [
            TranscriptionResult(
                text="Live video audio transcribed into text",
                start_time=0.0,
                end_time=2.0,
                detected_language="en",
                confidence=0.99,
            )
        ]

    def get_model_info(self) -> dict:
        return {
            "model_name": "pipeline-mock",
            "device": "cpu",
            "compute_type": "int8",
            "is_loaded": True,
        }


def test_transcription_pipeline_end_to_end(
    test_db: DatabaseConnection,
    app_config: AppConfig,
    session_repo: SessionRepository,
    segment_repo: SegmentRepository,
    qapp: QApplication,
) -> None:
    """Verify that TranscriptionPipeline creates sessions, saves segments to SQLite, and finalizes cleanly."""
    audio_service = AudioCaptureService()
    mock_provider = PipelineMockProvider()

    pipeline = TranscriptionPipeline(
        config=app_config,
        session_repo=session_repo,
        segment_repo=segment_repo,
        audio_service=audio_service,
        speech_provider=mock_provider,
    )

    emitted_segments: list[TranscriptSegment] = []
    pipeline.segment_received.connect(lambda seg: emitted_segments.append(seg))

    # 1. Start pipeline session
    session = pipeline.start_session(
        title="Integration Test Session",
        source_type=AudioSourceType.SYSTEM_LOOPBACK,
    )
    assert session is not None
    assert pipeline.is_running is True

    # Verify session created in SQLite
    db_session = session_repo.get_by_id(session.id)
    assert db_session is not None
    assert db_session.title == "Integration Test Session"

    # 2. Simulate incoming audio chunk
    chunk = AudioChunk(
        data=np.ones(16000, dtype=np.float32),
        sample_rate=16000,
        start_time=0.0,
        end_time=3.0,
    )
    audio_service.audio_queue.put(chunk)

    # Allow worker to process
    t_end = time.time() + 1.0
    while time.time() < t_end and len(emitted_segments) == 0:
        qapp.processEvents()
        time.sleep(0.05)

    assert len(emitted_segments) == 1
    assert emitted_segments[0].original_text == "Live video audio transcribed into text"

    # Verify segment was persisted to SQLite
    persisted_segments = segment_repo.get_by_session(session.id)
    assert len(persisted_segments) == 1
    assert persisted_segments[0].id == emitted_segments[0].id
    assert persisted_segments[0].sequence_number == 1

    # 3. Stop pipeline session
    final_session = pipeline.stop_session()
    assert pipeline.is_running is False
    assert final_session.ended_at is not None
    assert final_session.duration_seconds >= 0.0

    # Verify updated session metadata in SQLite
    updated_session = session_repo.get_by_id(session.id)
    assert updated_session.ended_at is not None
