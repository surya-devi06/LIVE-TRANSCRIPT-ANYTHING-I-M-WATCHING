"""Pytest configuration and shared fixtures."""

import sys
from pathlib import Path
from typing import Generator
import pytest

# Ensure src is on sys.path for test execution
SRC_PATH = Path(__file__).resolve().parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from live_transcript.config import AppConfig
from live_transcript.database.connection import DatabaseConnection
from live_transcript.database.migrations import MigrationRunner
from live_transcript.database.repositories import (
    SegmentRepository,
    SessionRepository,
    SettingsRepository,
    VocabularyRepository,
)


@pytest.fixture
def temp_data_dir(tmp_path: Path) -> Path:
    """Provide a clean temporary directory for application storage."""
    data_dir = tmp_path / "app_data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@pytest.fixture
def app_config(temp_data_dir: Path) -> AppConfig:
    """Provide an AppConfig instance isolated to the temporary directory."""
    return AppConfig(data_dir=temp_data_dir)


@pytest.fixture
def test_db(temp_data_dir: Path) -> DatabaseConnection:
    """Provide a migrated, isolated SQLite database connection."""
    db_path = temp_data_dir / "test_live_transcript.db"
    db = DatabaseConnection(db_path)
    runner = MigrationRunner(db)
    runner.run_migrations()
    return db


@pytest.fixture
def session_repo(test_db: DatabaseConnection) -> SessionRepository:
    return SessionRepository(test_db)


@pytest.fixture
def segment_repo(test_db: DatabaseConnection) -> SegmentRepository:
    return SegmentRepository(test_db)


@pytest.fixture
def vocab_repo(test_db: DatabaseConnection) -> VocabularyRepository:
    return VocabularyRepository(test_db)


@pytest.fixture
def settings_repo(test_db: DatabaseConnection) -> SettingsRepository:
    return SettingsRepository(test_db)
