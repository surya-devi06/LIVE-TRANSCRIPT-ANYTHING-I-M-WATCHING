"""Unit tests for Windows WASAPI audio device enumeration."""

import pytest
from live_transcript.audio.device_manager import DeviceManager


def test_device_manager_enumeration() -> None:
    """DeviceManager should enumerate WASAPI loopback playback devices."""
    dm = DeviceManager()
    loopbacks = dm.get_playback_loopback_devices()
    assert isinstance(loopbacks, list)

    # On this Windows 11 machine, loopback devices are available
    if loopbacks:
        for dev in loopbacks:
            assert dev.is_loopback is True
            assert isinstance(dev.name, str)
            assert dev.channels > 0


def test_device_manager_microphone_enumeration() -> None:
    """DeviceManager should enumerate physical microphone devices."""
    dm = DeviceManager()
    mics = dm.get_microphone_devices()
    assert isinstance(mics, list)
    for mic in mics:
        assert mic.is_loopback is False
        assert isinstance(mic.name, str)


def test_device_manager_fallback_behavior() -> None:
    """Non-existent device ID should safely fall back to the default device."""
    dm = DeviceManager()
    raw_device = dm.get_raw_device_by_id("non_existent_device_id_12345", is_loopback=True)
    # If any loopback devices exist, fallback should return a valid device object
    loopbacks = dm.get_playback_loopback_devices()
    if loopbacks:
        assert raw_device is not None
