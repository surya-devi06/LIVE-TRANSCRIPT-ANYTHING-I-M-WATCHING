"""Unit tests for thread-safe BoundedAudioQueue and AudioChunkAccumulator."""

import numpy as np
import pytest

from live_transcript.audio.audio_buffer import AudioChunk, AudioChunkAccumulator, BoundedAudioQueue


def test_bounded_audio_queue_overflow() -> None:
    """Queue should drop the oldest chunk when capacity is exceeded."""
    queue = BoundedAudioQueue(max_size=5)

    for i in range(10):
        chunk = AudioChunk(
            data=np.array([float(i)], dtype=np.float32),
            sample_rate=16000,
            start_time=float(i),
            end_time=float(i + 1),
        )
        queue.put(chunk)

    # Size should be clamped to max_size
    assert queue.size() == 5
    assert queue.dropped_chunks == 5
    assert queue.total_chunks_pushed == 10

    # Oldest retained chunk should be chunk index 5
    oldest = queue.get(timeout=0.1)
    assert oldest is not None
    assert oldest.data[0] == 5.0


def test_bounded_audio_queue_clear() -> None:
    """Clear should reset the queue size to zero."""
    queue = BoundedAudioQueue(max_size=10)
    queue.put(AudioChunk(data=np.zeros(10), sample_rate=16000, start_time=0.0, end_time=1.0))
    assert queue.size() == 1
    queue.clear()
    assert queue.is_empty() is True
    assert queue.size() == 0


def test_chunk_accumulator_windowing() -> None:
    """Accumulator should slice incoming stream into exact 3.0s (48000 samples @ 16kHz) chunks."""
    acc = AudioChunkAccumulator(target_sample_rate=16000, chunk_duration_seconds=3.0)
    target_samples = 16000 * 3  # 48000 samples

    # Add 1 second of samples (16000 samples) -> should not produce chunk yet
    chunks1 = acc.add_samples(np.zeros(16000, dtype=np.float32))
    assert len(chunks1) == 0

    # Add 2.5 seconds of samples (40000 samples) -> total 56000 samples -> 1 chunk produced, 8000 left
    chunks2 = acc.add_samples(np.zeros(40000, dtype=np.float32))
    assert len(chunks2) == 1
    assert len(chunks2[0].data) == target_samples
    assert chunks2[0].start_time == 0.0
    assert chunks2[0].end_time == 3.0

    # Flush the remaining 8000 samples (0.5s)
    final_chunk = acc.flush()
    assert final_chunk is not None
    assert len(final_chunk.data) == 8000
    assert final_chunk.start_time == 3.0
    assert final_chunk.end_time == 3.5

    # Second flush should return None
    assert acc.flush() is None
