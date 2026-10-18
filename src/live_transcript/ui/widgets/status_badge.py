"""Visual status indicator badge widget."""

from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from live_transcript.constants import AppState


class StatusBadge(QWidget):
    """Badge widget displaying a colored indicator dot and state label."""

    _COLOR_MAP = {
        AppState.READY: ("#10B981", "#064E3B", "#6EE7B7"),        # Green
        AppState.INITIALIZING: ("#F59E0B", "#78350F", "#FCD34D"), # Amber
        AppState.CAPTURING: ("#3B82F6", "#1E3A8A", "#93C5FD"),    # Blue
        AppState.TRANSCRIBING: ("#8B5CF6", "#4C1D95", "#C4B5FD"), # Purple
        AppState.PAUSED: ("#F59E0B", "#78350F", "#FDE68A"),       # Amber
        AppState.STOPPED: ("#64748B", "#1E293B", "#CBD5E1"),      # Slate
        AppState.ERROR: ("#EF4444", "#7F1D1D", "#FCA5A5"),        # Red
    }

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._current_state = AppState.READY

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 10, 4)
        layout.setSpacing(6)

        # Indicator dot
        self._dot = QLabel("●", self)
        self._dot.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Text label
        self._text_label = QLabel(self._current_state.value, self)
        self._text_label.setStyleSheet("font-weight: 600; font-size: 12px;")

        layout.addWidget(self._dot)
        layout.addWidget(self._text_label)

        self.set_state(AppState.READY)

    def set_state(self, state: AppState, custom_text: Optional[str] = None) -> None:
        """Update badge appearance according to the runtime state."""
        self._current_state = state
        dot_color, bg_color, text_color = self._COLOR_MAP.get(
            state, ("#64748B", "#1E293B", "#CBD5E1")
        )

        display_text = custom_text or state.value
        self._text_label.setText(display_text)
        self._dot.setStyleSheet(f"color: {dot_color}; font-size: 11px;")
        self._text_label.setStyleSheet(f"color: {text_color}; font-weight: 600; font-size: 12px;")

        self.setStyleSheet(
            f"""
            StatusBadge {{
                background-color: {bg_color};
                border: 1px solid {dot_color};
                border-radius: 12px;
            }}
            """
        )

    @property
    def current_state(self) -> AppState:
        return self._current_state
