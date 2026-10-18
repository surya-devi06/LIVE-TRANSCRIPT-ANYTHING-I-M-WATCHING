"""Application configuration manager and settings definitions."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from live_transcript.constants import (
    AudioSourceType,
    DisplayMode,
    ThemeMode,
)
from live_transcript.utils.platform_utils import get_default_data_dir


@dataclass
class AppConfig:
    """Runtime application configuration."""

    # Paths
    data_dir: Path = field(default_factory=get_default_data_dir)
    db_path: Path = field(init=False)
    log_dir: Path = field(init=False)
    models_dir: Path = field(init=False)
    exports_dir: Path = field(init=False)

    # Logging
    log_level: str = "INFO"

    # Audio & Transcription Settings
    audio_source: AudioSourceType = AudioSourceType.SYSTEM_LOOPBACK
    selected_audio_device: Optional[str] = None
    transcription_provider: str = "local_whisper"
    model_name: str = "base"
    source_language: str = "auto"
    target_language: str = "en"
    chunk_duration_seconds: float = 3.0

    # UI Settings
    theme: ThemeMode = ThemeMode.DARK
    font_size: int = 14
    auto_scroll: bool = True
    display_mode: DisplayMode = DisplayMode.ORIGINAL_ONLY

    # Privacy Settings
    local_only_mode: bool = True

    def __post_init__(self) -> None:
        """Derive paths and ensure storage directories exist."""
        self.db_path = self.data_dir / "live_transcript.db"
        self.log_dir = self.data_dir / "logs"
        self.models_dir = self.data_dir / "models"
        self.exports_dir = self.data_dir / "exports"

        # Ensure directories exist
        for directory in (self.data_dir, self.log_dir, self.models_dir, self.exports_dir):
            directory.mkdir(parents=True, exist_ok=True)


def load_config(env_path: Optional[Path] = None, data_dir: Optional[Path] = None) -> AppConfig:
    """Load configuration from environment variables, .env file, and defaults."""
    if env_path and env_path.is_file():
        load_dotenv(dotenv_path=env_path)
    else:
        # Default check for .env in current working directory
        load_dotenv()

    # Determine data directory
    custom_data_dir = os.environ.get("LIVE_TRANSCRIPT_DATA_DIR")
    resolved_data_dir = data_dir or (Path(custom_data_dir) if custom_data_dir else get_default_data_dir())

    log_level = os.environ.get("LIVE_TRANSCRIPT_LOG_LEVEL", "INFO")

    return AppConfig(
        data_dir=resolved_data_dir,
        log_level=log_level,
    )
