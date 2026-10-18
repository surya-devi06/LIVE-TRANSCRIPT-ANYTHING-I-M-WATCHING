"""Dialog for first-time AI model download with disk space verification and progress."""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from live_transcript.transcription.model_manager import ModelManager, ModelSpec
from live_transcript.utils.logging_setup import get_logger

logger = get_logger("ui.dialogs.model_download")


class _DownloadWorker(QThread):
    """Background worker thread executing faster_whisper.download_model."""

    finished_status = Signal(bool, str)  # (success: bool, message: str)

    def __init__(self, model_name: str, models_dir: Path, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.model_name = model_name
        self.models_dir = models_dir

    def run(self) -> None:
        try:
            import faster_whisper
            logger.info("Starting download of model '%s' into %s...", self.model_name, self.models_dir)
            faster_whisper.download_model(
                self.model_name,
                output_dir=str(self.models_dir),
            )
            self.finished_status.emit(True, "Model downloaded successfully.")
        except Exception as exc:
            logger.error("Failed to download model '%s': %s", self.model_name, exc)
            self.finished_status.emit(False, str(exc))


class ModelDownloadDialog(QDialog):
    """Dialog providing transparent disk checks, progress, and download execution for Whisper models."""

    def __init__(
        self,
        model_name: str,
        models_dir: Path,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.model_name = model_name
        self.models_dir = models_dir
        self.spec: ModelSpec = ModelManager.get_spec(model_name)
        self._worker: Optional[_DownloadWorker] = None
        self.download_succeeded: bool = False

        self.setWindowTitle(f"AI Model Setup — Whisper {self.spec.name.capitalize()}")
        self.resize(520, 360)
        self.setModal(True)

        self._setup_ui()
        self._verify_disk_space()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header Title
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        lbl_title = QLabel(f"Download Speech Model: {self.spec.display_name}", self)
        lbl_title.setStyleSheet("font-size: 17px; font-weight: 700; color: #F8FAFC;")
        lbl_desc = QLabel(
            "Live Transcript processes speech locally on your computer. "
            "To begin transcription, the required offline Whisper model must be downloaded once and cached locally.",
            self,
        )
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #94A3B8; font-size: 13px; line-height: 1.4;")
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_desc)
        layout.addLayout(title_box)

        # Details Card
        info_card = QFrame(self)
        info_card.setStyleSheet("background-color: #1E293B; border-radius: 8px; padding: 12px; border: 1px solid #334155;")
        ic_layout = QVBoxLayout(info_card)
        ic_layout.setSpacing(8)

        lbl_specs = QLabel(
            f"• <b>Download Size:</b> ~{self.spec.size_mb} MB<br>"
            f"• <b>Storage Required:</b> ~{self.spec.required_free_mb} MB free disk space<br>"
            f"• <b>Performance:</b> {self.spec.description}",
            info_card,
        )
        lbl_specs.setStyleSheet("color: #CBD5E1; font-size: 12px;")
        ic_layout.addWidget(lbl_specs)
        layout.addWidget(info_card)

        # Disk Space Check Status
        self.lbl_disk_status = QLabel("Checking disk space...", self)
        self.lbl_disk_status.setStyleSheet("font-size: 12px; color: #38BDF8; font-weight: 500;")
        layout.addWidget(self.lbl_disk_status)

        # Progress Bar & Operation Status
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #0F172A;
                border-radius: 4px;
                border: 1px solid #334155;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284C7, stop:1 #38BDF8);
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)

        self.lbl_op_status = QLabel("Ready to download.", self)
        self.lbl_op_status.setStyleSheet("font-size: 12px; color: #94A3B8;")
        layout.addWidget(self.lbl_op_status)

        layout.addStretch()

        # Action Buttons
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(12)

        self.btn_cancel = QPushButton("Cancel", self)
        self.btn_cancel.clicked.connect(self.reject)
        btn_bar.addWidget(self.btn_cancel)

        btn_bar.addStretch()

        self.btn_action = QPushButton("Start Download", self)
        self.btn_action.setProperty("class", "primary-btn")
        self.btn_action.setStyleSheet("min-width: 130px; font-weight: 600;")
        self.btn_action.clicked.connect(self._start_download)
        btn_bar.addWidget(self.btn_action)

        layout.addLayout(btn_bar)

    def _verify_disk_space(self) -> None:
        has_space, free_mb, required_mb = ModelManager.check_disk_space(self.models_dir, self.model_name)
        if has_space:
            self.lbl_disk_status.setText(f"✓ Sufficient disk space: {free_mb:,} MB free on disk (Need {required_mb} MB).")
            self.lbl_disk_status.setStyleSheet("font-size: 12px; color: #34D399; font-weight: 500;")
            self.btn_action.setEnabled(True)
        else:
            self.lbl_disk_status.setText(f"⚠️ Insufficient disk space: Only {free_mb:,} MB free. Need at least {required_mb} MB.")
            self.lbl_disk_status.setStyleSheet("font-size: 12px; color: #F87171; font-weight: 500;")
            self.btn_action.setEnabled(False)

    def _start_download(self) -> None:
        self.btn_action.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.btn_cancel.setText("Cancel")
        self.progress_bar.setRange(0, 0)  # Pulse mode
        self.lbl_op_status.setText("Connecting to Hugging Face repository and downloading model weights...")
        self.lbl_op_status.setStyleSheet("font-size: 12px; color: #38BDF8;")

        self._worker = _DownloadWorker(self.model_name, self.models_dir, self)
        self._worker.finished_status.connect(self._on_download_finished)
        self._worker.start()

    def _on_download_finished(self, success: bool, message: str) -> None:
        self.progress_bar.setRange(0, 100)
        if success:
            self.download_succeeded = True
            self.progress_bar.setValue(100)
            self.lbl_op_status.setText("✓ Model download completed and verified!")
            self.lbl_op_status.setStyleSheet("font-size: 12px; color: #34D399; font-weight: 600;")
            self.btn_cancel.setVisible(False)
            self.btn_action.setEnabled(True)
            self.btn_action.setText("Continue")
            self.btn_action.clicked.disconnect()
            self.btn_action.clicked.connect(self.accept)
        else:
            self.download_succeeded = False
            self.progress_bar.setValue(0)
            self.lbl_op_status.setText(f"⚠️ Download failed: {message}")
            self.lbl_op_status.setStyleSheet("font-size: 12px; color: #F87171;")
            self.btn_action.setEnabled(True)
            self.btn_action.setText("Retry")
            self.btn_action.clicked.disconnect()
            self.btn_action.clicked.connect(self._start_download)

    def closeEvent(self, event) -> None:
        if self._worker and self._worker.isRunning():
            self._worker.terminate()
            self._worker.wait(1000)
        super().closeEvent(event)
