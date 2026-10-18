"""Settings screen organized into Audio, Transcription, AI, Interface, Privacy, and Advanced tabs."""

import os
from pathlib import Path
from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from live_transcript.config import AppConfig
from live_transcript.constants import (
    AVAILABLE_MODELS,
    SUPPORTED_LANGUAGES,
    AudioSourceType,
    DisplayMode,
    ThemeMode,
)
from live_transcript.database.repositories import SettingsRepository


class SettingsView(QWidget):
    """Configuration interface for audio, speech-recognition, AI, and display preferences."""

    theme_changed = Signal(ThemeMode)
    settings_saved = Signal()

    def __init__(
        self,
        config: AppConfig,
        settings_repo: SettingsRepository,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.config = config
        self.settings_repo = settings_repo

        self._setup_ui()
        self.load_settings()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Header Title
        title = QLabel("Settings", self)
        title.setProperty("class", "view-title")
        desc = QLabel("Configure audio input, speech-recognition models, interface, and privacy options.", self)
        desc.setProperty("class", "view-desc")
        layout.addWidget(title)
        layout.addWidget(desc)

        # Tab Widget
        self.tabs = QTabWidget(self)

        # 1. Audio Tab
        tab_audio = QWidget()
        audio_layout = QFormLayout(tab_audio)
        audio_layout.setContentsMargins(16, 16, 16, 16)
        audio_layout.setSpacing(12)

        self.audio_source_combo = QComboBox(tab_audio)
        self.audio_source_combo.addItem("System Audio (WASAPI Loopback)", AudioSourceType.SYSTEM_LOOPBACK.value)
        self.audio_source_combo.addItem("Microphone Input", AudioSourceType.MICROPHONE.value)
        audio_layout.addRow("Default Audio Source:", self.audio_source_combo)

        self.playback_device_combo = QComboBox(tab_audio)
        self.playback_device_combo.addItem("Default Playback Device", "")
        audio_layout.addRow("Playback Output Device:", self.playback_device_combo)

        self.audio_rate_combo = QComboBox(tab_audio)
        self.audio_rate_combo.addItems(["16000 Hz (Whisper Native)", "44100 Hz", "48000 Hz (Windows Default)"])
        audio_layout.addRow("Audio Sample Rate:", self.audio_rate_combo)

        audio_info = QLabel("System Loopback captures computer playback without needing a microphone.", tab_audio)
        audio_info.setStyleSheet("color: #94A3B8; font-size: 12px;")
        audio_layout.addRow("", audio_info)

        self.tabs.addTab(tab_audio, "🎙  Audio")

        # 2. Transcription Tab
        tab_transcription = QWidget()
        trans_layout = QFormLayout(tab_transcription)
        trans_layout.setContentsMargins(16, 16, 16, 16)
        trans_layout.setSpacing(12)

        self.model_combo = QComboBox(tab_transcription)
        for model in AVAILABLE_MODELS:
            self.model_combo.addItem(model.capitalize(), model)
        trans_layout.addRow("Recognition Model:", self.model_combo)

        self.src_lang_combo = QComboBox(tab_transcription)
        for code, label in SUPPORTED_LANGUAGES.items():
            self.src_lang_combo.addItem(label, code)
        trans_layout.addRow("Spoken Language:", self.src_lang_combo)

        self.chunk_spin = QSpinBox(tab_transcription)
        self.chunk_spin.setRange(1, 10)
        self.chunk_spin.setSuffix(" seconds")
        self.chunk_spin.setValue(int(self.config.chunk_duration_seconds))
        trans_layout.addRow("Chunk Duration:", self.chunk_spin)

        self.tabs.addTab(tab_transcription, "⚡  Transcription")

        # 3. AI Assistance Tab
        tab_ai = QWidget()
        ai_layout = QFormLayout(tab_ai)
        ai_layout.setContentsMargins(16, 16, 16, 16)
        ai_layout.setSpacing(12)

        self.target_lang_combo = QComboBox(tab_ai)
        for code, label in SUPPORTED_LANGUAGES.items():
            if code != "auto":
                self.target_lang_combo.addItem(label, code)
        ai_layout.addRow("Translation Target Language:", self.target_lang_combo)

        self.api_key_input = QLineEdit(tab_ai)
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Optional API key for cloud translation/grammar...")
        ai_layout.addRow("AI Provider API Key:", self.api_key_input)

        ai_note = QLabel("API keys are never stored in plain text and are not required for local transcription.", tab_ai)
        ai_note.setStyleSheet("color: #94A3B8; font-size: 12px;")
        ai_layout.addRow("", ai_note)

        self.tabs.addTab(tab_ai, "🌐  AI & Translation")

        # 4. Interface Tab
        tab_interface = QWidget()
        ui_layout = QFormLayout(tab_interface)
        ui_layout.setContentsMargins(16, 16, 16, 16)
        ui_layout.setSpacing(12)

        self.theme_combo = QComboBox(tab_interface)
        self.theme_combo.addItem("Dark Theme (Default)", ThemeMode.DARK.value)
        self.theme_combo.addItem("Light Theme", ThemeMode.LIGHT.value)
        ui_layout.addRow("Application Theme:", self.theme_combo)

        self.font_spin = QSpinBox(tab_interface)
        self.font_spin.setRange(11, 24)
        self.font_spin.setValue(self.config.font_size)
        self.font_spin.setSuffix(" pt")
        ui_layout.addRow("Transcript Font Size:", self.font_spin)

        self.tabs.addTab(tab_interface, "🎨  Interface")

        # 5. Privacy Tab
        tab_privacy = QWidget()
        privacy_layout = QVBoxLayout(tab_privacy)
        privacy_layout.setContentsMargins(16, 16, 16, 16)
        privacy_layout.setSpacing(12)

        self.chk_local_only = QCheckBox("Enforce Local-Only Mode (Never send audio or text to cloud)", tab_privacy)
        self.chk_local_only.setChecked(self.config.local_only_mode)
        privacy_layout.addWidget(self.chk_local_only)

        priv_box = QFrame(tab_privacy)
        priv_box.setProperty("class", "card")
        p_box_layout = QVBoxLayout(priv_box)
        lbl_p_title = QLabel("Privacy Guarantee", priv_box)
        lbl_p_title.setStyleSheet("font-weight: 600; color: #10B981;")
        lbl_p_desc = QLabel(
            "• System loopback audio is processed entirely in memory on your device.\n"
            "• No audio streams are saved to disk permanently by default.\n"
            "• Database storage resides strictly at your local profile directory.",
            priv_box,
        )
        lbl_p_desc.setStyleSheet("color: #94A3B8; font-size: 12px; line-height: 1.5;")
        p_box_layout.addWidget(lbl_p_title)
        p_box_layout.addWidget(lbl_p_desc)
        privacy_layout.addWidget(priv_box)
        privacy_layout.addStretch()

        self.tabs.addTab(tab_privacy, "🔒  Privacy")

        # 6. Advanced Tab
        tab_advanced = QWidget()
        adv_layout = QVBoxLayout(tab_advanced)
        adv_layout.setContentsMargins(16, 16, 16, 16)
        adv_layout.setSpacing(12)

        btn_open_data = QPushButton("📁  Open Application Data Folder", tab_advanced)
        btn_open_data.clicked.connect(lambda: os.startfile(str(self.config.data_dir)))
        btn_open_logs = QPushButton("📄  Open Logs Folder", tab_advanced)
        btn_open_logs.clicked.connect(lambda: os.startfile(str(self.config.log_dir)))

        adv_layout.addWidget(btn_open_data)
        adv_layout.addWidget(btn_open_logs)
        adv_layout.addStretch()

        self.tabs.addTab(tab_advanced, "⚙  Advanced")

        layout.addWidget(self.tabs)

        # Save Button Bar
        btn_bar = QHBoxLayout()
        btn_bar.addStretch()
        self.btn_save = QPushButton("Save Settings", self)
        self.btn_save.setProperty("class", "primary-btn")
        self.btn_save.setMinimumWidth(130)
        self.btn_save.clicked.connect(self.save_settings)
        btn_bar.addWidget(self.btn_save)

        layout.addLayout(btn_bar)

    def set_devices(self, loopback_devices: list, mic_devices: list) -> None:
        """Populate the playback devices combo."""
        self.playback_device_combo.blockSignals(True)
        self.playback_device_combo.clear()
        self.playback_device_combo.addItem("Default Playback Device", "")
        for dev in loopback_devices:
            label = dev.name + (" (Default)" if dev.is_default else "")
            self.playback_device_combo.addItem(label, dev.id)
        self.playback_device_combo.blockSignals(False)

        # Restore selected device if saved
        saved_dev = self.settings_repo.get("selected_audio_device", "")
        idx = self.playback_device_combo.findData(saved_dev)
        if idx >= 0:
            self.playback_device_combo.setCurrentIndex(idx)

    def load_settings(self) -> None:
        """Load persisted settings into UI fields."""
        theme_val = self.settings_repo.get("theme", self.config.theme.value)
        idx = self.theme_combo.findData(theme_val)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)

        model_val = self.settings_repo.get("model_name", self.config.model_name)
        idx = self.model_combo.findData(model_val)
        if idx >= 0:
            self.model_combo.setCurrentIndex(idx)

        src_val = self.settings_repo.get("source_language", self.config.source_language)
        idx = self.src_lang_combo.findData(src_val)
        if idx >= 0:
            self.src_lang_combo.setCurrentIndex(idx)

        tgt_val = self.settings_repo.get("target_language", self.config.target_language)
        idx = self.target_lang_combo.findData(tgt_val)
        if idx >= 0:
            self.target_lang_combo.setCurrentIndex(idx)

        dev_val = self.settings_repo.get("selected_audio_device", "")
        idx = self.playback_device_combo.findData(dev_val)
        if idx >= 0:
            self.playback_device_combo.setCurrentIndex(idx)

        chunk_val = self.settings_repo.get("chunk_duration_seconds", str(self.config.chunk_duration_seconds))
        try:
            self.chunk_spin.setValue(int(float(chunk_val)))
        except ValueError:
            pass

    def save_settings(self) -> None:
        """Persist UI settings values to SQLite database and notify listeners."""
        theme_val = self.theme_combo.currentData()
        model_val = self.model_combo.currentData()
        src_val = self.src_lang_combo.currentData()
        tgt_val = self.target_lang_combo.currentData()
        dev_val = self.playback_device_combo.currentData() or ""
        chunk_val = str(self.chunk_spin.value())
        local_only = "1" if self.chk_local_only.isChecked() else "0"

        self.settings_repo.set("theme", theme_val)
        self.settings_repo.set("model_name", model_val)
        self.settings_repo.set("source_language", src_val)
        self.settings_repo.set("target_language", tgt_val)
        self.settings_repo.set("selected_audio_device", dev_val)
        self.settings_repo.set("chunk_duration_seconds", chunk_val)
        self.settings_repo.set("local_only_mode", local_only)

        self.config.theme = ThemeMode(theme_val)
        self.config.model_name = model_val
        self.config.source_language = src_val
        self.config.target_language = tgt_val
        self.config.selected_audio_device = dev_val if dev_val else None
        self.config.chunk_duration_seconds = float(self.chunk_spin.value())
        self.config.local_only_mode = (local_only == "1")

        self.theme_changed.emit(self.config.theme)
        self.settings_saved.emit()

        QMessageBox.information(self, "Settings Saved", "Your preferences have been saved successfully.")
