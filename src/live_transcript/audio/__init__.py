"""Audio capture, device management, buffering, and preprocessing module."""

from live_transcript.audio.audio_buffer import AudioChunkAccumulator, BoundedAudioQueue
from live_transcript.audio.capture import AudioCaptureService
from live_transcript.audio.device_manager import AudioDeviceInfo, DeviceManager
from live_transcript.audio.preprocessing import (
    AudioPreprocessor,
    calculate_rms_and_level,
    convert_to_mono,
    is_silent,
    resample_audio,
)

__all__ = [
    "AudioDeviceInfo",
    "DeviceManager",
    "AudioPreprocessor",
    "BoundedAudioQueue",
    "AudioChunkAccumulator",
    "AudioCaptureService",
    "convert_to_mono",
    "resample_audio",
    "calculate_rms_and_level",
    "is_silent",
]
