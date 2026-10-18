"""Unit tests for TranscriptionWorker thread lifecycle and segment dispatch."""

import time
import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from live_transcript.audio.audio_buffer import AudioChunk, BoundedAudioQueue
from live_transcript.database.models import TranscriptSegment
from live_transcript.transcription.base import SpeechRecognitionProvider, TranscriptionResult
from live_transcript.transcription.worker import TranscriptionWorker


class MockWorkerProvider(SpeechRecognitionProvider):
    def __init__(self) -> None:
        self._loaded = True

    def load_model(self) -> None:
        self._loaded = True

    def is_loaded(self) -> bool:
        return self._loaded

    def transcribe(self, audio: np.ndarray, language=None) -> list[TranscriptionResult]:
        return [
            TranscriptionResult(
                text="Test recognized transcript chunk",
                start_time=0.0,
                end_time=3.0,
                detected_language="en",
                confidence=0.98,
            )
        ]

    def get_model_info(self) -> dict:
        return {
            "model_name": "mock",
            "device": "cpu",
            "compute_type": "float32",
            "is_loaded": True,
        }


def test_transcription_worker_processing(qapp: QApplication) -> None:
    """Worker should consume audio chunks and emit TranscriptSegment with accurate sequence."""
    queue = BoundedAudioQueue(max_size=10)
    provider = MockWorkerProvider()

    worker = TranscriptionWorker(
        provider=provider,
        audio_queue=queue,
        session_id="test_session_123",
        source_language="en",
    )

    received_segments: list[TranscriptSegment] = []
    worker.segment_ready.connect(lambda seg: received_segments.append(seg))

    # Push two audio chunks
    queue.put(
        AudioChunk(
            data=np.ones(16000, dtype=np.float32),
            sample_rate=16000,
            start_time=0.0,
            end_time=3.0,
        )
    )
    queue.put(
        AudioChunk(
            data=np.ones(16000, dtype=np.float32),
            sample_rate=16000,
            start_time=3.0,
            end_time=6.0,
        )
    )

    worker.start()
    assert worker.is_running is True

    # Process events for up to 1 second
    t_end = time.time() + 1.0
    while time.time() < t_end and len(received_segments) < 2:
        qapp.processEvents()
        time.sleep(0.05)

    worker.stop()
    assert worker.is_running is False
    assert len(received_segments) == 2

    # Verify segment #1
    s1 = received_segments[0]
    assert s1.session_id == "test_session_123"
    assert s1.sequence_number == 1
    assert s1.start_time == 0.0
    assert s1.end_time == 3.0
    assert s1.original_text == "Test recognized transcript chunk"

    # Verify segment #2
    s2 = received_segments[1]
    assert s2.session_id == "test_session_123"
    assert s2.sequence_number == 2
    assert s2.start_time == 3.0
    assert s2.end_time == 6.0


def test_transcription_worker_pause_resume(qapp: QApplication) -> None:
    """Paused worker should not process new chunks until resumed."""
    queue = BoundedAudioQueue(max_size=10)
    provider = MockWorkerProvider()

    worker = TranscriptionWorker(
        provider=provider,
        audio_queue=queue,
        session_id="pause_session",
    )

    received_segments: list[TranscriptSegment] = []
    worker.segment_ready.connect(lambda seg: received_segments.append(seg))

    worker.start()
    worker.pause()
    time.sleep(0.08)

    # Put a chunk while paused
    queue.put(
        AudioChunk(
            data=np.ones(16000, dtype=np.float32),
            sample_rate=16000,
            start_time=0.0,
            end_time=1.0,
        )
    )

    # Process events while paused: chunk should not be consumed
    t_end = time.time() + 0.3
    while time.time() < t_end:
        qapp.processEvents()
        time.sleep(0.05)

    assert len(received_segments) == 0

    # Resume worker
    worker.resume()
    t_end = time.time() + 0.5
    while time.time() < t_end and len(received_segments) == 0:
        qapp.processEvents()
        time.sleep(0.05)

    worker.stop()
    assert len(received_segments) == 1
