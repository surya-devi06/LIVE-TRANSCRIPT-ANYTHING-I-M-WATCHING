"""Integration test for AudioCaptureService with live WASAPI loopback capture."""

import time
import pytest
from PySide6.QtWidgets import QApplication

from live_transcript.audio.capture import AudioCaptureService
from live_transcript.audio.device_manager import DeviceManager
from live_transcript.constants import AppState, AudioSourceType


def test_audio_capture_service_lifecycle(qapp: QApplication) -> None:
    """Test start, level updates, pause, resume, and clean stop of AudioCaptureService."""
    app = qapp

    dm = DeviceManager()
    loopbacks = dm.get_playback_loopback_devices()
    if not loopbacks:
        pytest.skip("No WASAPI loopback audio playback devices available in this test environment.")

    # Configure short chunk duration (1.0s) for rapid integration testing
    service = AudioCaptureService(device_manager=dm, chunk_duration=1.0)
    service.set_source(AudioSourceType.SYSTEM_LOOPBACK)

    states_recorded: list[AppState] = []
    levels_recorded: list[float] = []

    service.state_changed.connect(lambda state, msg: states_recorded.append(state))
    service.level_meter_updated.connect(lambda level, db: levels_recorded.append(level))

    # 1. Start capture
    started = service.start()
    assert started is True

    # Run event loop for 1.2 seconds to capture frames
    t_end = time.time() + 1.2
    while time.time() < t_end:
        app.processEvents()
        time.sleep(0.05)

    assert service.current_state in (AppState.INITIALIZING, AppState.CAPTURING)
    assert len(levels_recorded) > 0

    # 2. Test Pause
    service.pause()
    assert service.current_state == AppState.PAUSED

    # 3. Test Resume
    service.resume()
    assert service.current_state == AppState.CAPTURING

    # 4. Test Clean Stop
    service.stop()
    assert service.current_state == AppState.STOPPED
    assert service._thread is None or not service._thread.is_alive()
