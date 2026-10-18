"""Real-time audio level meter widget with gradient peak visualization and smooth decay."""

from typing import Optional
from PySide6.QtCore import QRectF, QTimer, Qt
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPaintEvent
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget


class AudioLevelMeter(QWidget):
    """Visual horizontal audio level meter bar with dB readout and peak decay."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(22)
        self.setMinimumWidth(160)

        self._current_level: float = 0.0
        self._target_level: float = 0.0
        self._peak_level: float = 0.0
        self._current_db: float = -60.0

        # Decay animation timer (running at ~40 FPS for fluid meter falloff)
        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(25)
        self._anim_timer.timeout.connect(self._animate_decay)
        self._anim_timer.start()

    def set_level(self, linear_level: float, rms_db: float) -> None:
        """Update current audio level (linear 0.0-1.0 and dBFS)."""
        self._target_level = max(0.0, min(1.0, linear_level))
        self._current_db = rms_db

        if self._target_level > self._current_level:
            self._current_level = self._target_level
        if self._target_level > self._peak_level:
            self._peak_level = self._target_level

        self.update()

    def reset(self) -> None:
        """Reset meter to silence."""
        self._target_level = 0.0
        self._current_level = 0.0
        self._peak_level = 0.0
        self._current_db = -60.0
        self.update()

    def _animate_decay(self) -> None:
        """Smoothly decay meter bar and peak indicator downwards."""
        needs_update = False
        decay_rate = 0.04

        if self._current_level > self._target_level:
            self._current_level = max(self._target_level, self._current_level - decay_rate)
            needs_update = True

        if self._peak_level > 0.0:
            self._peak_level = max(0.0, self._peak_level - (decay_rate * 0.4))
            needs_update = True

        if needs_update:
            self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        # 1. Background slot
        bg_rect = QRectF(0, 2, width, height - 4)
        painter.setBrush(QColor("#1A1C23"))
        painter.setPen(QColor("#282C35"))
        painter.drawRoundedRect(bg_rect, 4, 4)

        # 2. Active level fill
        meter_width = (width - 4) * self._current_level
        if meter_width > 1:
            fill_rect = QRectF(2, 4, meter_width, height - 8)

            # Gradient: Green -> Yellow -> Red
            gradient = QLinearGradient(0, 0, width, 0)
            gradient.setColorAt(0.0, QColor("#10B981"))   # Green
            gradient.setColorAt(0.70, QColor("#10B981"))  # Green up to -18dB
            gradient.setColorAt(0.85, QColor("#F59E0B"))  # Yellow around -9dB
            gradient.setColorAt(1.0, QColor("#EF4444"))   # Red near 0dB

            painter.setBrush(gradient)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(fill_rect, 3, 3)

        # 3. Peak indicator bar
        if self._peak_level > 0.02:
            peak_x = 2 + (width - 4) * self._peak_level
            painter.setPen(QColor("#F8FAFC"))
            painter.drawLine(int(peak_x), 3, int(peak_x), height - 4)

        # 4. dB text overlay
        db_text = f"{int(self._current_db):+3d} dB" if self._current_level > 0.02 else "— dB"
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        painter.setPen(QColor("#94A3B8"))
        painter.drawText(bg_rect.adjusted(0, 0, -6, 0), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, db_text)
