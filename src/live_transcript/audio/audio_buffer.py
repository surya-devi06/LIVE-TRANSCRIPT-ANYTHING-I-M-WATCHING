"""Thread-safe bounded audio ring buffer and chunk accumulator."""

from collections import deque
from dataclasses import dataclass
import threading
import time
from typing import Deque, List, Optional
import numpy as np

from live_transcript.utils.logging_setup import get_logger

logger = get_logger("audio.buffer")


@dataclass
class AudioChunk:
    """Represents a discrete audio chunk ready for inference or feature extraction."""
    data: np.ndarray
    sample_rate: int
    start_time: float
    end_time: float


class BoundedAudioQueue:
    """Thread-safe bounded FIFO audio queue with explicit backpressure handling.

    When the queue reaches max_size, new additions safely drop the oldest chunk
    to prevent memory growth, incrementing the dropped_chunks counter.
    """

    def __init__(self, max_size: int = 50) -> None:
        self.max_size = max(5, max_size)
        self._deque: Deque[AudioChunk] = deque(maxlen=self.max_size)
        self._lock = threading.Lock()
        self._not_empty = threading.Condition(self._lock)
        self.dropped_chunks: int = 0
        self.total_chunks_pushed: int = 0

    def put(self, chunk: AudioChunk) -> bool:
        """Push a new audio chunk into the queue.

        Returns True if placed normally, or False if an older chunk was dropped due to overflow.
        """
        dropped = False
        with self._lock:
            if len(self._deque) >= self.max_size:
                self.dropped_chunks += 1
                dropped = True
                if self.dropped_chunks % 10 == 1:
                    logger.warning(
                        "Audio buffer overflow! Dropping oldest chunk (Total dropped: %d). "
                        "Transcription worker may be running behind.",
                        self.dropped_chunks,
                    )
            self._deque.append(chunk)
            self.total_chunks_pushed += 1
            self._not_empty.notify()

        return not dropped

    def get(self, timeout: Optional[float] = 0.5) -> Optional[AudioChunk]:
        """Pop the oldest chunk from the queue, blocking up to timeout seconds."""
        with self._not_empty:
            if not self._deque:
                if not self._not_empty.wait(timeout=timeout):
                    return None
            if self._deque:
                return self._deque.popleft()
            return None

    def clear(self) -> None:
        """Flush all chunks from the queue."""
        with self._lock:
            self._deque.clear()

    def size(self) -> int:
        """Return current number of chunks waiting in queue."""
        with self._lock:
            return len(self._deque)

    def is_empty(self) -> bool:
        """Return True if queue contains no chunks."""
        with self._lock:
            return len(self._deque) == 0

    def get_stats(self) -> dict:
        """Return queue statistics."""
        with self._lock:
            return {
                "size": len(self._deque),
                "max_size": self.max_size,
                "total_pushed": self.total_chunks_pushed,
                "dropped_chunks": self.dropped_chunks,
            }


class AudioChunkAccumulator:
    """Accumulates variable-length raw audio frames into standardized fixed-duration chunks."""

    def __init__(
        self,
        target_sample_rate: int = 16000,
        chunk_duration_seconds: float = 3.0,
    ) -> None:
        self.target_sample_rate = target_sample_rate
        self.chunk_duration_seconds = chunk_duration_seconds
        self.target_chunk_samples = int(target_sample_rate * chunk_duration_seconds)

        self._buffer: List[float] = []
        self._current_session_time: float = 0.0

    def reset(self) -> None:
        """Reset internal accumulator buffer and session time."""
        self._buffer.clear()
        self._current_session_time = 0.0

    def add_samples(self, samples: np.ndarray) -> List[AudioChunk]:
        """Add preprocessed 16kHz mono samples and return any completed chunks."""
        if len(samples) == 0:
            return []

        self._buffer.extend(samples.tolist())
        ready_chunks: List[AudioChunk] = []

        while len(self._buffer) >= self.target_chunk_samples:
            chunk_data = np.array(self._buffer[:self.target_chunk_samples], dtype=np.float32)
            self._buffer = self._buffer[self.target_chunk_samples:]

            start_t = self._current_session_time
            end_t = start_t + self.chunk_duration_seconds
            self._current_session_time = end_t

            ready_chunks.append(
                AudioChunk(
                    data=chunk_data,
                    sample_rate=self.target_sample_rate,
                    start_time=start_t,
                    end_time=end_t,
                )
            )

        return ready_chunks

    def flush(self) -> Optional[AudioChunk]:
        """Flush any remaining buffered samples as a final partial chunk if non-empty."""
        if not self._buffer:
            return None

        chunk_data = np.array(self._buffer, dtype=np.float32)
        duration = len(self._buffer) / self.target_sample_rate
        start_t = self._current_session_time
        end_t = start_t + duration
        self._current_session_time = end_t
        self._buffer.clear()

        return AudioChunk(
            data=chunk_data,
            sample_rate=self.target_sample_rate,
            start_time=start_t,
            end_time=end_t,
        )
