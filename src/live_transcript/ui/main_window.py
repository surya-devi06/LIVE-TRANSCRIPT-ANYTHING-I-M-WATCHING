"""Main application window with header, sidebar navigation, and stacked view switching."""

from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from live_transcript.config import AppConfig
from live_transcript.constants import (
    APP_NAME,
    APP_VERSION,
    AppState,
    AudioSourceType,
    DEFAULT_WINDOW_TITLE,
    ThemeMode,
)
from live_transcript.database.connection import DatabaseConnection
from live_transcript.database.repositories import (
    SegmentRepository,
    SessionRepository,
    SettingsRepository,
    VocabularyRepository,
)
from live_transcript.audio.capture import AudioCaptureService
from live_transcript.audio.device_manager import DeviceManager
from live_transcript.transcription.local_whisper import LocalWhisperProvider
from live_transcript.transcription.model_manager import ModelManager
from live_transcript.transcription.pipeline import TranscriptionPipeline
from live_transcript.ui.dialogs.model_download_dialog import ModelDownloadDialog
from live_transcript.ui.styles import get_theme_stylesheet
from live_transcript.ui.views.about_view import AboutView
from live_transcript.ui.views.dashboard import DashboardView
from live_transcript.ui.views.history_view import HistoryView
from live_transcript.ui.views.live_transcript import LiveTranscriptView
from live_transcript.ui.views.settings_view import SettingsView
from live_transcript.ui.views.vocabulary_view import VocabularyView
from live_transcript.ui.widgets.status_badge import StatusBadge
from live_transcript.utils.logging_setup import get_logger

logger = get_logger("ui.main_window")


class MainWindow(QMainWindow):
    """Main window hosting header, navigation sidebar, and content views."""

    def __init__(
        self,
        config: AppConfig,
        db: DatabaseConnection,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.config = config
        self.db = db

        # Initialize repositories
        self.session_repo = SessionRepository(self.db)
        self.segment_repo = SegmentRepository(self.db)
        self.vocab_repo = VocabularyRepository(self.db)
        self.settings_repo = SettingsRepository(self.db)

        # Initialize audio services & speech recognition pipeline
        self.device_manager = DeviceManager()
        self.audio_service = AudioCaptureService(
            device_manager=self.device_manager,
            chunk_duration=self.config.chunk_duration_seconds,
            parent=self,
        )
        self.speech_provider = LocalWhisperProvider(
            model_name=self.config.model_name,
            download_root=self.config.models_dir,
        )
        self.pipeline = TranscriptionPipeline(
            config=self.config,
            session_repo=self.session_repo,
            segment_repo=self.segment_repo,
            audio_service=self.audio_service,
            speech_provider=self.speech_provider,
            parent=self,
        )

        self.setWindowTitle(DEFAULT_WINDOW_TITLE)
        self.resize(1150, 750)
        self.setMinimumSize(960, 600)

        self._setup_ui()
        self._init_audio_devices()
        self.apply_theme(self.config.theme)
        logger.info("MainWindow initialized successfully.")

    def _setup_ui(self) -> None:
        # Main central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Top Header Bar
        header = self._create_header()
        root_layout.addWidget(header)

        # 2. Body: Sidebar + Views Stack
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # Sidebar
        sidebar = self._create_sidebar()
        body_layout.addWidget(sidebar)

        # Stacked Views
        self.view_stack = QStackedWidget(self)
        self.view_stack.setObjectName("CentralStack")

        # Instantiate Views
        self.dashboard_view = DashboardView(self.config, self.session_repo, self.view_stack)
        self.live_view = LiveTranscriptView(
            segment_repo=self.segment_repo,
            vocab_repo=self.vocab_repo,
            parent=self.view_stack,
        )
        self.history_view = HistoryView(
            session_repo=self.session_repo,
            segment_repo=self.segment_repo,
            vocab_repo=self.vocab_repo,
            parent=self.view_stack,
        )
        self.vocab_view = VocabularyView(self.vocab_repo, self.view_stack)
        self.settings_view = SettingsView(self.config, self.settings_repo, self.view_stack)
        self.about_view = AboutView(self.view_stack)

        self.view_stack.addWidget(self.dashboard_view)    # Index 0
        self.view_stack.addWidget(self.live_view)         # Index 1
        self.view_stack.addWidget(self.history_view)      # Index 2
        self.view_stack.addWidget(self.vocab_view)        # Index 3
        self.view_stack.addWidget(self.settings_view)     # Index 4
        self.view_stack.addWidget(self.about_view)        # Index 5

        body_layout.addWidget(self.view_stack, stretch=1)
        root_layout.addLayout(body_layout)

        # Wire up inter-view signals
        self._wire_signals()

    def _create_header(self) -> QFrame:
        header = QFrame(self)
        header.setObjectName("HeaderBar")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(16)

        # App branding
        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        title_box.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        lbl_title = QLabel(APP_NAME, header)
        lbl_title.setObjectName("HeaderTitle")
        lbl_sub = QLabel(f"v{APP_VERSION} • Real-Time AI Audio Transcription", header)
        lbl_sub.setObjectName("HeaderSubtitle")
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)
        layout.addLayout(title_box)

        layout.addStretch()

        # Audio source badge
        self.lbl_active_source = QLabel("🎙  System Loopback", header)
        self.lbl_active_source.setStyleSheet(
            "background-color: #1E293B; color: #94A3B8; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;"
        )
        layout.addWidget(self.lbl_active_source)

        # Status badge
        self.status_badge = StatusBadge(header)
        layout.addWidget(self.status_badge)

        # Settings shortcut icon button
        btn_settings_shortcut = QPushButton("⚙", header)
        btn_settings_shortcut.setFixedSize(32, 32)
        btn_settings_shortcut.setStyleSheet("padding: 0; font-size: 16px; border-radius: 16px;")
        btn_settings_shortcut.clicked.connect(lambda: self.switch_view(4))
        layout.addWidget(btn_settings_shortcut)

        return header

    def _create_sidebar(self) -> QWidget:
        sidebar = QWidget(self)
        sidebar.setObjectName("SidebarWidget")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 12, 0, 12)
        layout.setSpacing(4)

        self.nav_group = QButtonGroup(sidebar)
        self.nav_group.setExclusive(True)

        nav_items = [
            ("📊  Dashboard", 0),
            ("🎙  Live Transcript", 1),
            ("🕒  History", 2),
            ("📖  Vocabulary", 3),
            ("⚙  Settings", 4),
            ("ℹ  About", 5),
        ]

        self.nav_buttons: list[QPushButton] = []
        for label, idx in nav_items:
            btn = QPushButton(label, sidebar)
            btn.setProperty("class", "nav-btn")
            btn.setCheckable(True)
            self.nav_group.addButton(btn, idx)
            layout.addWidget(btn)
            self.nav_buttons.append(btn)

        self.nav_buttons[0].setChecked(True)
        self.nav_group.idClicked.connect(self.switch_view)

        layout.addStretch()
        return sidebar

    def _init_audio_devices(self) -> None:
        """Enumerate audio devices and populate UI controls."""
        try:
            loopbacks = self.device_manager.get_playback_loopback_devices()
            mics = self.device_manager.get_microphone_devices()

            self.live_view.set_devices(loopbacks, mics)
            self.settings_view.set_devices(loopbacks, mics)

            default_dev = self.device_manager.get_default_loopback_device()
            if default_dev:
                self.dashboard_view.set_device_info(default_dev.name)
                self.lbl_active_source.setText(f"🎙  {default_dev.name[:25]}")
            else:
                self.dashboard_view.set_device_info("No playback loopback detected")
        except Exception as exc:
            logger.error("Failed to initialize audio devices in UI: %s", exc)

    def _wire_signals(self) -> None:
        # Dashboard actions
        self.dashboard_view.request_start_session.connect(self._on_dashboard_start)
        self.dashboard_view.request_navigate_settings.connect(lambda: self.switch_view(4))
        self.dashboard_view.request_open_session.connect(self._open_session_in_history)

        # Settings theme & update
        self.settings_view.theme_changed.connect(self.apply_theme)
        self.settings_view.settings_saved.connect(self._on_settings_saved)

        # Audio source & device updates
        self.live_view.source_changed.connect(self._on_audio_source_changed)
        self.live_view.device_changed.connect(self._on_audio_device_changed)

        # Live transcript capture controls
        self.live_view.start_clicked.connect(self._start_transcription)
        self.live_view.pause_clicked.connect(self._pause_resume_transcription)
        self.live_view.stop_clicked.connect(self._stop_transcription)

        # Pipeline signals
        self.pipeline.level_meter_updated.connect(self._on_audio_level_updated)
        self.pipeline.pipeline_state_changed.connect(self._on_pipeline_state_changed)
        self.pipeline.status_message.connect(self.live_view.set_status_message)
        self.pipeline.segment_received.connect(self.live_view.add_segment)
        self.pipeline.error_occurred.connect(self._on_pipeline_error)
        self.pipeline.session_ended.connect(self._on_session_ended)

        # History open session
        self.history_view.session_selected.connect(self._open_session_in_history)

        # Cross-view vocabulary refresh
        self.live_view.vocabulary_added.connect(lambda _: self.vocab_view.refresh())
        self.history_view.vocabulary_added.connect(lambda _: self.vocab_view.refresh())

        # Sync pipeline session to live view
        self.pipeline.session_started.connect(lambda s: self.live_view.set_session_id(s.id))

    def _start_transcription(self) -> None:
        """Start capturing audio and live speech recognition pipeline."""
        logger.info("Starting transcription pipeline from LiveTranscriptView...")

        # 1. Verify model is available locally, or prompt first-run downloader
        if not ModelManager.is_model_downloaded(self.config.models_dir, self.config.model_name):
            dialog = ModelDownloadDialog(
                model_name=self.config.model_name,
                models_dir=self.config.models_dir,
                parent=self,
            )
            if not dialog.exec() or not dialog.download_succeeded:
                logger.info("Model download was cancelled by user. Halting transcription start.")
                self.live_view._handle_stop()
                return

        item = self.live_view.combo_source.currentData()
        dev_id = ""
        source_type = AudioSourceType.SYSTEM_LOOPBACK
        if item:
            dev_id, source_type = item

        session = self.pipeline.start_session(
            source_type=source_type,
            device_id=dev_id if dev_id else None,
        )
        if session:
            self.live_view.set_session_id(session.id)

    def _pause_resume_transcription(self) -> None:
        """Toggle pause/resume on the transcription pipeline."""
        if self.live_view._is_paused:
            self.pipeline.pause()
        else:
            self.pipeline.resume()

    def _stop_transcription(self) -> None:
        """Stop transcription pipeline and refresh history and dashboard."""
        logger.info("Stopping transcription pipeline from LiveTranscriptView...")
        self.pipeline.stop_session()
        self.live_view.set_status_message("", visible=False)
        self.dashboard_view.refresh_data()
        self.history_view.refresh()

    def _on_session_ended(self, session) -> None:
        """Handle session finalization."""
        self.dashboard_view.refresh_data()
        self.history_view.refresh()

    def _on_audio_device_changed(self, device_id: str, source_type: AudioSourceType) -> None:
        """Update audio capture service configured device."""
        self.audio_service.set_source(source_type, device_id=device_id if device_id else None)

    def _on_audio_level_updated(self, linear_level: float, rms_db: float) -> None:
        """Forward real-time audio levels to the active meters."""
        self.live_view.set_audio_level(linear_level, rms_db)
        self.dashboard_view.set_audio_level(linear_level, rms_db)

    def _on_pipeline_state_changed(self, state: AppState, message: str) -> None:
        """Reflect pipeline state on the header status badge."""
        self.status_badge.set_state(state, custom_text=state.value)

    def _on_pipeline_error(self, error_message: str) -> None:
        """Handle pipeline errors."""
        self.status_badge.set_state(AppState.ERROR, "Error")
        self.live_view.set_status_message(f"⚠️ {error_message}")
        logger.error("Pipeline error reported: %s", error_message)

    def _on_settings_saved(self) -> None:
        """Apply updated configuration parameters to audio service and model."""
        saved_dev = self.config.selected_audio_device
        self.audio_service.set_source(self.config.audio_source, device_id=saved_dev)
        self.audio_service.chunk_duration = self.config.chunk_duration_seconds

        if self.speech_provider.model_name != self.config.model_name:
            self.speech_provider.model_name = self.config.model_name
            if not ModelManager.is_model_downloaded(self.config.models_dir, self.config.model_name):
                dialog = ModelDownloadDialog(
                    model_name=self.config.model_name,
                    models_dir=self.config.models_dir,
                    parent=self,
                )
                dialog.exec()

        self.dashboard_view.lbl_model.setText(f"• Model: {self.config.model_name.capitalize()} (Local)")
        self.dashboard_view.refresh_data()

    def switch_view(self, view_index: int) -> None:
        """Switch active screen in the QStackedWidget."""
        if 0 <= view_index < self.view_stack.count():
            self.view_stack.setCurrentIndex(view_index)
            btn = self.nav_group.button(view_index)
            if btn and not btn.isChecked():
                btn.setChecked(True)

            if view_index == 0:
                self.dashboard_view.refresh_data()
            elif view_index == 2:
                self.history_view.refresh()
            elif view_index == 3:
                self.vocab_view.refresh()

    def _on_dashboard_start(self) -> None:
        """Quick start action from dashboard."""
        self.switch_view(1)
        self.live_view._handle_start()

    def _open_session_in_history(self, session_id: str) -> None:
        """Switch to History view and open the specified session."""
        self.switch_view(2)
        self.history_view.open_session(session_id)
        logger.info("Opened session details for session ID: %s", session_id)

    def _on_audio_source_changed(self, source_type: AudioSourceType) -> None:
        if source_type == AudioSourceType.MICROPHONE:
            self.lbl_active_source.setText("🎤  Microphone")
        else:
            self.lbl_active_source.setText("🎙  System Loopback")

    def apply_theme(self, theme: ThemeMode) -> None:
        """Apply Qt Style Sheet across the entire application."""
        qss = get_theme_stylesheet(theme)
        self.setStyleSheet(qss)
        logger.debug("Applied theme: %s", theme.value)

    def closeEvent(self, event) -> None:
        """Safely release audio and transcription resources on application close."""
        logger.info("MainWindow closeEvent triggered. Releasing pipeline resources...")
        try:
            self.pipeline.stop_session()
        except Exception as exc:
            logger.warning("Error stopping pipeline on window close: %s", exc)
        event.accept()
