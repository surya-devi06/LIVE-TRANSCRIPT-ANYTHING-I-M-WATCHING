"""About and legal/privacy view."""

from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from live_transcript.constants import APP_NAME, APP_VERSION


class AboutView(QWidget):
    """About dialog showing application details, architecture, and legal/privacy statements."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(24, 20, 24, 20)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Title & Version
        title = QLabel(f"{APP_NAME} v{APP_VERSION}", content)
        title.setProperty("class", "view-title")
        subtitle = QLabel("Real-Time AI Transcription, Translation & Language Learning", content)
        subtitle.setProperty("class", "view-desc")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Overview Card
        card_overview = QFrame(content)
        card_overview.setProperty("class", "card")
        co_layout = QVBoxLayout(card_overview)
        lbl_arch = QLabel(
            "<b>Architecture Highlights:</b><br>"
            "• <b>Audio Capture:</b> Direct Windows WASAPI loopback capture without requiring microphones.<br>"
            "• <b>Speech Recognition:</b> Local Faster-Whisper / CTranslate2 with CPU fallback and NVIDIA GPU acceleration.<br>"
            "• <b>Storage:</b> Local SQLite database using WAL (Write-Ahead Logging) and versioned schema migrations.<br>"
            "• <b>Desktop UI:</b> PySide6 (Qt 6) with asynchronous worker threads and signals/slots separation.",
            card_overview,
        )
        lbl_arch.setWordWrap(True)
        lbl_arch.setStyleSheet("line-height: 1.6; color: #CBD5E1;")
        co_layout.addWidget(lbl_arch)
        layout.addWidget(card_overview)

        # Privacy & Compliance Notice Card
        card_privacy = QFrame(content)
        card_privacy.setProperty("class", "card")
        cp_layout = QVBoxLayout(card_privacy)
        lbl_prv_head = QLabel("Privacy, Security & Lawful Usage Notice", card_privacy)
        lbl_prv_head.setStyleSheet("font-weight: 700; color: #38BDF8; font-size: 14px;")
        lbl_prv_text = QLabel(
            "1. <b>Local Processing:</b> Live audio captured from your computer is processed locally in memory. "
            "No audio files are saved permanently or uploaded without explicit user configuration.<br><br>"
            "2. <b>Lawful Transcription:</b> This software is designed for transcribing and learning from media, "
            "lectures, and streams where you have the legal right or permission to listen and transcribe. "
            "It does not attempt to bypass DRM, copyright protection, access controls, or application security mechanisms.<br><br>"
            "3. <b>Third-Party Cloud APIs:</b> If you configure external cloud translation or LLM keys, "
            "only the relevant text segments are dispatched to the selected provider according to their privacy terms.",
            card_privacy,
        )
        lbl_prv_text.setWordWrap(True)
        lbl_prv_text.setStyleSheet("line-height: 1.5; color: #94A3B8; font-size: 13px;")
        cp_layout.addWidget(lbl_prv_head)
        cp_layout.addWidget(lbl_prv_text)
        layout.addWidget(card_privacy)

        layout.addStretch()
        scroll.setWidget(content)
        outer_layout.addWidget(scroll)
