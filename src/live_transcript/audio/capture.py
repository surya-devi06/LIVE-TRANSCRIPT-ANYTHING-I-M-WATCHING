"""Audio capture service managing Windows WASAPI loopback and microphone recording threads."""

import threading
import time
from typing import Optional
import numpy as np
from PySide6.QtCore import QObject, Signal

from live_transcript.audio.audio_buffer import AudioChunk, AudioChunkAccumulator, BoundedAudioQueue
from live_transcript.audio.device_manager import DeviceManager
from live_transcript.audio.preprocessing import AudioPreprocessor, calculate_rms_and_level
from live_transcript.constants import AppState, AudioSourceType
from live_transcript.utils.logging_setup import get_logger

logger = get_logger("audio.capture")


class AudioCaptureService(QObject):
    """Background service managing the lifecycle of WASAPI loopback audio capture."""

    # Qt Signals for UI communication
    level_meter_updated = Signal(float, float)  # (linear_level: 0.0-1.0, rms_db: -60 to 0)
    chunk_ready = Signal(object)                 # (chunk: AudioChunk)
    state_changed = Signal(object, str)          # (state: AppState, message: str)
    error_occurred = Signal(str)                 # (error_message: str)

    def __init__(
        self,
        device_manager: Optional[DeviceManager] = None,
        chunk_duration: float = 3.0,
        target_sample_rate: int = 16000,
        queue_max_size: int = 50,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)
        self.device_manager = device_manager or DeviceManager()
        self.chunk_duration = chunk_duration
        self.target_sample_rate = target_sample_rate

        self.audio_queue = BoundedAudioQueue(max_size=queue_max_size)
        self.preprocessor = AudioPreprocessor(target_sample_rate=target_sample_rate)
        self.accumulator = AudioChunkAccumulator(
            target_sample_rate=target_sample_rate,
            chunk_duration_seconds=chunk_duration,
        )

        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()  # Unpaused by default

        self._current_state = AppState.READY
        self._source_type = AudioSourceType.SYSTEM_LOOPBACK
        self._selected_device_id: Optional[str] = None

    @property
    def current_state(self) -> AppState:
        return self._current_state

    def set_source(self, source_type: AudioSourceType, device_id: Optional[str] = None) -> None:
        """Configure input source and optional specific device ID."""
        self._source_type = source_type
        self._selected_device_id = device_id
        logger.info("Configured audio source: %s (Device: %s)", source_type.value, device_id)

    def start(self) -> bool:
        """Start background audio capture thread."""
        if self._thread and self._thread.is_alive():
            logger.warning("Audio capture already running.")
            return True

        self._stop_event.clear()
        self._pause_event.set()
        self.audio_queue.clear()
        self.accumulator.reset()

        self._set_state(AppState.INITIALIZING, "Initializing audio capture...")

        self._thread = threading.Thread(
            target=self._capture_worker,
            name="AudioCaptureWorker",
            daemon=True,
        )
        self._thread.start()
        return True

    def pause(self) -> None:
        """Pause audio capture."""
        if self._current_state == AppState.CAPTURING:
            self._pause_event.clear()
            self._set_state(AppState.PAUSED, "Audio capture paused.")
            self.level_meter_updated.emit(0.0, -60.0)

    def resume(self) -> None:
        """Resume paused audio capture."""
        if self._current_state == AppState.PAUSED:
            self._pause_event.set()
            self._set_state(AppState.CAPTURING, "Audio capture running.")

    def stop(self) -> None:
        """Stop background audio capture thread and release resources."""
        if not self._thread or not self._thread.is_alive():
            self._set_state(AppState.STOPPED, "Stopped.")
            self.level_meter_updated.emit(0.0, -60.0)
            return

        logger.info("Stopping audio capture thread...")
        self._stop_event.set()
        self._pause_event.set()  # Unblock if paused

        self._thread.join(timeout=3.0)
        if self._thread.is_alive():
            logger.warning("Audio capture thread did not terminate within timeout.")

        # Flush any remaining partial audio chunk
        final_chunk = self.accumulator.flush()
        if final_chunk:
            self.audio_queue.put(final_chunk)
            self.chunk_ready.emit(final_chunk)

        self.level_meter_updated.emit(0.0, -60.0)
        self._set_state(AppState.STOPPED, "Audio capture stopped.")
        logger.info("Audio capture stopped cleanly.")

    def _set_state(self, state: AppState, message: str = "") -> None:
        self._current_state = state
        self.state_changed.emit(state, message)

    def _capture_worker(self) -> None:
        """Background thread executing loopback or microphone recording."""
        is_loopback = (self._source_type == AudioSourceType.SYSTEM_LOOPBACK)
        raw_device = self.device_manager.get_raw_device_by_id(
            device_id=self._selected_device_id,
            is_loopback=is_loopback,
        )

        if not raw_device:
            err_msg = (
                f"No suitable {'playback loopback' if is_loopback else 'microphone'} device found."
            )
            logger.error(err_msg)
            self.error_occurred.emit(err_msg)
            self._set_state(AppState.ERROR, err_msg)
            return

        logger.info(
            "Acquiring audio stream on device: %s (Channels: %d, Loopback: %s)",
            raw_device.name,
            raw_device.channels,
            is_loopback,
        )

        # Standard sample rates to attempt
        sample_rate = 48000
        block_duration = 0.1  # 100ms blocks
        block_size = int(sample_rate * block_duration)

        try:
            with raw_device.recorder(samplerate=sample_rate, channels=raw_device.channels) as rec:
                self._set_state(AppState.CAPTURING, f"Capturing from {raw_device.name}")
                logger.info("Audio capture stream opened successfully.")

                while not self._stop_event.is_set():
                    # Handle paused state
                    if not self._pause_event.is_set():
                        time.sleep(0.05)
                        continue

                    # Record a block of frames (blocks for ~100ms)
                    data = rec.record(numframes=block_size)
                    if data is None or len(data) == 0:
                        continue

                    # 1. Calculate live meter levels
                    rms_db, linear_level = calculate_rms_and_level(data)
                    self.level_meter_updated.emit(linear_level, rms_db)

                    # 2. Preprocess: convert to mono and resample to 16kHz
                    processed_samples = self.preprocessor.process(
                        raw_audio=data,
                        source_sample_rate=sample_rate,
                    )

                    # 3. Accumulate samples into target chunks
                    new_chunks = self.accumulator.add_samples(processed_samples)
                    for chunk in new_chunks:
                        self.audio_queue.put(chunk)
                        self.chunk_ready.emit(chunk)

        except Exception as exc:
            err_msg = f"Audio capture stream error on {raw_device.name}: {exc}"
            logger.exception(err_msg)
            self.error_occurred.emit(err_msg)
            self._set_state(AppState.ERROR, err_msg)
        finally:
            self.level_meter_updated.emit(0.0, -60.0)
            logger.info("Exiting audio capture worker thread.")
