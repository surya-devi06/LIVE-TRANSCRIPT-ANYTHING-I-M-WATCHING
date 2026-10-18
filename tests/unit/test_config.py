"""Unit tests for configuration and path resolution."""

import os
from pathlib import Path
from live_transcript.config import AppConfig, load_config
from live_transcript.constants import AudioSourceType, ThemeMode
from live_transcript.utils.platform_utils import sanitize_filename


def test_app_config_initialization(temp_data_dir: Path) -> None:
    """Verify AppConfig automatically sets up directories and paths."""
    config = AppConfig(data_dir=temp_data_dir)

    assert config.db_path == temp_data_dir / "live_transcript.db"
    assert config.log_dir == temp_data_dir / "logs"
    assert config.models_dir == temp_data_dir / "models"
    assert config.exports_dir == temp_data_dir / "exports"

    assert config.log_dir.is_dir()
    assert config.models_dir.is_dir()
    assert config.exports_dir.is_dir()
    assert config.audio_source == AudioSourceType.SYSTEM_LOOPBACK
    assert config.theme == ThemeMode.DARK
    assert config.local_only_mode is True


def test_load_config_with_custom_env(temp_data_dir: Path, monkeypatch) -> None:
    """Verify load_config respects environment variable overrides."""
    monkeypatch.setenv("LIVE_TRANSCRIPT_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("LIVE_TRANSCRIPT_DATA_DIR", str(temp_data_dir))

    cfg = load_config()
    assert cfg.log_level == "DEBUG"
    assert cfg.data_dir == temp_data_dir


def test_sanitize_filename() -> None:
    """Verify filenames with invalid characters are safely sanitized."""
    assert sanitize_filename('Meeting: "Q3 Review" <Live>?') == "Meeting_ _Q3 Review_ _Live__"
    assert sanitize_filename("   ...filename...   ") == "filename"
    assert sanitize_filename("") == "transcript"
