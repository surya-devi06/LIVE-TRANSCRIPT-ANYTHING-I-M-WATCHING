"""Test that MainWindow and UI views instantiate cleanly without runtime errors."""

import pytest
from PySide6.QtWidgets import QApplication

from live_transcript.config import AppConfig
from live_transcript.database.connection import DatabaseConnection
from live_transcript.ui.main_window import MainWindow
from live_transcript.constants import ThemeMode


def test_main_window_instantiation(test_db: DatabaseConnection, app_config: AppConfig, qapp: QApplication) -> None:
    """Verify that MainWindow and all view tabs instantiate without crashes."""
    window = MainWindow(config=app_config, db=test_db)
    assert window is not None
    assert window.view_stack.count() == 6

    # Verify tab navigation
    for idx in range(6):
        window.switch_view(idx)
        assert window.view_stack.currentIndex() == idx

    # Verify theme switching
    window.apply_theme(ThemeMode.LIGHT)
    window.apply_theme(ThemeMode.DARK)

    window.close()
