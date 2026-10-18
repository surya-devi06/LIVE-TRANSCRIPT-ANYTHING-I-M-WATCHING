"""Main dashboard view showcasing system readiness, quick start, and recent activity."""

from typing import Callable, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from live_transcript.config import AppConfig
from live_transcript.database.repositories import SessionRepository
from live_transcript.ui.widgets.audio_meter import AudioLevelMeter


class DashboardView(QWidget):
    """Main dashboard overview."""

    request_start_session = Signal()
    request_navigate_settings = Signal()
    request_open_session = Signal(str)

    def __init__(
        self,
        config: AppConfig,
        session_repo: SessionRepository,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.config = config
        self.session_repo = session_repo

        self._setup_ui()
        self.refresh_data()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Header Title
        title = QLabel("Dashboard", self)
        title.setProperty("class", "view-title")
        desc = QLabel(
            "Transcribe speech in real-time from videos, reels, meetings, and browser media.",
            self,
        )
        desc.setProperty("class", "view-desc")

        layout.addWidget(title)
        layout.addWidget(desc)

        # Quick Actions Card
        quick_card = QFrame(self)
        quick_card.setProperty("class", "card")
        quick_layout = QHBoxLayout(quick_card)
        quick_layout.setContentsMargins(16, 16, 16, 16)

        quick_text_box = QVBoxLayout()
        quick_headline = QLabel("Ready to capture live system audio?", quick_card)
        quick_headline.setStyleSheet("font-size: 16px; font-weight: 600; color: #F8FAFC;")
        quick_sub = QLabel(
            "Audio playing through your speakers or headphones will be transcribed live.",
            quick_card,
        )
        quick_sub.setStyleSheet("color: #94A3B8; font-size: 13px;")
        quick_text_box.addWidget(quick_headline)
        quick_text_box.addWidget(quick_sub)

        self.start_btn = QPushButton("▶  Start Live Transcription", quick_card)
        self.start_btn.setProperty("class", "primary-btn")
        self.start_btn.setMinimumHeight(42)
        self.start_btn.setMinimumWidth(220)
        self.start_btn.clicked.connect(self.request_start_session.emit)

        quick_layout.addLayout(quick_text_box, stretch=1)
        quick_layout.addWidget(self.start_btn)
        layout.addWidget(quick_card)

        # Status & Readiness Grid
        grid_layout = QGridLayout()
        grid_layout.setSpacing(16)

        # Card 1: Configuration & Model
        cfg_card = QFrame(self)
        cfg_card.setProperty("class", "card")
        cfg_box = QVBoxLayout(cfg_card)
        cfg_title = QLabel("Transcription Engine", cfg_card)
        cfg_title.setProperty("class", "section-header")
        self.lbl_model = QLabel(f"• Model: {self.config.model_name.capitalize()} (Local)", cfg_card)
        self.lbl_source = QLabel(f"• Input Source: {self.config.audio_source.value}", cfg_card)
        self.lbl_lang = QLabel(f"• Language: {self.config.source_language.upper()} → {self.config.target_language.upper()}", cfg_card)
        cfg_box.addWidget(cfg_title)
        cfg_box.addWidget(self.lbl_model)
        cfg_box.addWidget(self.lbl_source)
        cfg_box.addWidget(self.lbl_lang)
        cfg_box.addStretch()

        # Card 2: System Health Checklist
        health_card = QFrame(self)
        health_card.setProperty("class", "card")
        health_box = QVBoxLayout(health_card)
        health_title = QLabel("System Readiness", health_card)
        health_title.setProperty("class", "section-header")

        self.lbl_db_status = QLabel("✓ Local SQLite Storage: Connected", health_card)
        self.lbl_db_status.setStyleSheet("color: #10B981; font-weight: 500;")
        self.lbl_wasapi = QLabel("✓ Windows Loopback: Ready", health_card)
        self.lbl_wasapi.setStyleSheet("color: #10B981; font-weight: 500;")
        self.lbl_device = QLabel("• Active Device: Detecting...", health_card)
        self.lbl_device.setStyleSheet("color: #94A3B8; font-size: 12px;")

        # Live audio meter
        meter_label = QLabel("Audio Input Level:", health_card)
        meter_label.setStyleSheet("color: #CBD5E1; font-size: 11px; margin-top: 4px;")
        self.audio_meter = AudioLevelMeter(health_card)

        health_box.addWidget(health_title)
        health_box.addWidget(self.lbl_db_status)
        health_box.addWidget(self.lbl_wasapi)
        health_box.addWidget(self.lbl_device)
        health_box.addWidget(meter_label)
        health_box.addWidget(self.audio_meter)
        health_box.addStretch()

        grid_layout.addWidget(cfg_card, 0, 0)
        grid_layout.addWidget(health_card, 0, 1)
        layout.addLayout(grid_layout)

        # Recent Sessions Section
        recent_header = QLabel("Recent Sessions", self)
        recent_header.setProperty("class", "section-header")
        layout.addWidget(recent_header)

        self.recent_container = QFrame(self)
        self.recent_container.setProperty("class", "card")
        self.recent_layout = QVBoxLayout(self.recent_container)
        self.recent_layout.setContentsMargins(12, 12, 12, 12)
        layout.addWidget(self.recent_container)

        layout.addStretch()

    def refresh_data(self) -> None:
        """Refresh dynamic information like recent sessions from database."""
        # Clear existing items in recent sessions
        while self.recent_layout.count():
            item = self.recent_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        recent_sessions = self.session_repo.list_recent(limit=3)
        if not recent_sessions:
            empty_lbl = QLabel(
                "No previous sessions found. Click 'Start Live Transcription' above to begin your first session.",
                self.recent_container,
            )
            empty_lbl.setStyleSheet("color: #94A3B8; font-style: italic; padding: 12px 0;")
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.recent_layout.addWidget(empty_lbl)
        else:
            for session in recent_sessions:
                row = QWidget(self.recent_container)
                row_layout = QHBoxLayout(row)
                row_layout.setContentsMargins(4, 6, 4, 6)

                s_title = QLabel(session.title, row)
                s_title.setStyleSheet("font-weight: 600; color: #F1F5F9;")
                s_meta = QLabel(
                    f"{session.started_at[:19]} | {session.duration_seconds:.1f}s | {session.source_language}",
                    row,
                )
                s_meta.setStyleSheet("color: #94A3B8; font-size: 12px;")

                btn_view = QPushButton("Open", row)
                btn_view.setMaximumWidth(70)
                btn_view.clicked.connect(lambda _, s_id=session.id: self.request_open_session.emit(s_id))

                row_layout.addWidget(s_title, stretch=1)
                row_layout.addWidget(s_meta)
                row_layout.addWidget(btn_view)
                self.recent_layout.addWidget(row)

    def set_device_info(self, device_name: str) -> None:
        """Update displayed active device name."""
        self.lbl_device.setText(f"• Active Device: {device_name}")

    def set_audio_level(self, linear_level: float, rms_db: float) -> None:
        """Pass audio levels to the dashboard audio meter."""
        self.audio_meter.set_level(linear_level, rms_db)

