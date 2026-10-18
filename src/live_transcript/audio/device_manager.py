"""Audio device enumeration and selection manager using Windows WASAPI."""

from dataclasses import dataclass
from typing import Any, List, Optional
import soundcard as sc

from live_transcript.utils.logging_setup import get_logger

logger = get_logger("audio.device_manager")


@dataclass
class AudioDeviceInfo:
    """Represents an enumerated audio device."""
    id: str
    name: str
    is_loopback: bool
    channels: int
    is_default: bool = False


class DeviceManager:
    """Manages audio device enumeration and matching for WASAPI playback loopback and microphones."""

    def __init__(self) -> None:
        pass

    def get_playback_loopback_devices(self) -> List[AudioDeviceInfo]:
        """Enumerate all available playback devices in WASAPI loopback capture mode."""
        devices: List[AudioDeviceInfo] = []
        default_speaker_name = ""
        try:
            default_spk = sc.default_speaker()
            if default_spk:
                default_speaker_name = default_spk.name
        except Exception as exc:
            logger.warning("Could not determine default speaker: %s", exc)

        try:
            loopback_mics = [m for m in sc.all_microphones(include_loopback=True) if m.isloopback]
            for m in loopback_mics:
                is_default = (m.name == default_speaker_name)
                # Strip leading/trailing whitespaces
                clean_name = m.name.strip()
                devices.append(
                    AudioDeviceInfo(
                        id=m.id,
                        name=clean_name,
                        is_loopback=True,
                        channels=m.channels,
                        is_default=is_default,
                    )
                )
        except Exception as exc:
            logger.error("Failed to enumerate WASAPI loopback devices: %s", exc)

        return devices

    def get_microphone_devices(self) -> List[AudioDeviceInfo]:
        """Enumerate all available physical microphone input devices."""
        devices: List[AudioDeviceInfo] = []
        default_mic_name = ""
        try:
            default_mic = sc.default_microphone()
            if default_mic:
                default_mic_name = default_mic.name
        except Exception as exc:
            logger.warning("Could not determine default microphone: %s", exc)

        try:
            physical_mics = [m for m in sc.all_microphones(include_loopback=False) if not m.isloopback]
            for m in physical_mics:
                is_default = (m.name == default_mic_name)
                devices.append(
                    AudioDeviceInfo(
                        id=m.id,
                        name=m.name.strip(),
                        is_loopback=False,
                        channels=m.channels,
                        is_default=is_default,
                    )
                )
        except Exception as exc:
            logger.error("Failed to enumerate microphone devices: %s", exc)

        return devices

    def get_default_loopback_device(self) -> Optional[AudioDeviceInfo]:
        """Get the default Windows playback device configured for loopback capture."""
        loopbacks = self.get_playback_loopback_devices()
        for dev in loopbacks:
            if dev.is_default:
                return dev
        return loopbacks[0] if loopbacks else None

    def get_raw_device_by_id(self, device_id: Optional[str] = None, is_loopback: bool = True) -> Optional[Any]:
        """Retrieve raw soundcard device handle by device ID or return the default device."""
        try:
            all_devices = sc.all_microphones(include_loopback=is_loopback)
            if is_loopback:
                candidates = [m for m in all_devices if m.isloopback]
            else:
                candidates = [m for m in all_devices if not m.isloopback]

            if not candidates:
                return None

            if device_id:
                for dev in candidates:
                    if dev.id == device_id or dev.name == device_id:
                        return dev

            # Fallback to default
            if is_loopback:
                default_spk = sc.default_speaker()
                if default_spk:
                    for dev in candidates:
                        if dev.name == default_spk.name:
                            return dev
            else:
                return sc.default_microphone()

            return candidates[0]
        except Exception as exc:
            logger.error("Error retrieving raw soundcard device: %s", exc)
            return None
