"""Versioned SQLite schema migration runner."""

import sqlite3
from typing import Callable, List, Tuple

from live_transcript.database.connection import DatabaseConnection
from live_transcript.utils.logging_setup import get_logger

logger = get_logger("database.migrations")

# Type alias for a migration: (version, description, apply_callable)
Migration = Tuple[int, str, Callable[[sqlite3.Cursor], None]]


def _migration_001_initial_schema(cursor: sqlite3.Cursor) -> None:
    """Migration 001: Create core tables and indexes."""

    # Sessions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        started_at TEXT NOT NULL,
        ended_at TEXT,
        duration_seconds REAL NOT NULL DEFAULT 0.0,
        source_type TEXT NOT NULL DEFAULT 'System Audio',
        source_language TEXT NOT NULL DEFAULT 'auto',
        target_language TEXT NOT NULL DEFAULT 'en',
        transcription_provider TEXT NOT NULL DEFAULT 'local_whisper',
        model_name TEXT NOT NULL DEFAULT 'base',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    # Transcript segments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transcript_segments (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        sequence_number INTEGER NOT NULL,
        start_time REAL NOT NULL,
        end_time REAL NOT NULL,
        original_text TEXT NOT NULL,
        translated_text TEXT,
        detected_language TEXT,
        status TEXT NOT NULL DEFAULT 'final',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
    );
    """)

    # Vocabulary entries table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vocabulary_entries (
        id TEXT PRIMARY KEY,
        word_or_phrase TEXT NOT NULL,
        original_sentence TEXT NOT NULL,
        meaning TEXT NOT NULL,
        example_sentence TEXT,
        explanation_language TEXT NOT NULL DEFAULT 'en',
        source_session_id TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (source_session_id) REFERENCES sessions(id) ON DELETE SET NULL
    );
    """)

    # Key-value application settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS app_settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    # Indexes
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_segments_session_seq
    ON transcript_segments(session_id, sequence_number);
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_segments_session_start
    ON transcript_segments(session_id, start_time);
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_vocab_word
    ON vocabulary_entries(word_or_phrase);
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_sessions_created
    ON sessions(created_at);
    """)


MIGRATIONS: List[Migration] = [
    (1, "Initial schema: sessions, transcript_segments, vocabulary, settings", _migration_001_initial_schema),
]


class MigrationRunner:
    """Applies pending schema migrations sequentially."""

    def __init__(self, db: DatabaseConnection) -> None:
        self.db = db

    def _ensure_version_table(self, cursor: sqlite3.Cursor) -> None:
        """Create schema_version table if missing."""
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            description TEXT NOT NULL,
            applied_at TEXT NOT NULL DEFAULT (datetime('now', 'utc'))
        );
        """)

    def get_current_version(self) -> int:
        """Get the highest applied migration version."""
        with self.db.connect() as conn:
            cursor = conn.cursor()
            self._ensure_version_table(cursor)
            cursor.execute("SELECT COALESCE(MAX(version), 0) FROM schema_version;")
            row = cursor.fetchone()
            return int(row[0]) if row else 0

    def run_migrations(self) -> int:
        """Apply all pending migrations in order. Returns the current version."""
        current_version = self.get_current_version()
        logger.info("Current database schema version: %d", current_version)

        with self.db.transaction() as cursor:
            self._ensure_version_table(cursor)

            for version, description, apply_fn in MIGRATIONS:
                if version > current_version:
                    logger.info("Applying migration %03d: %s", version, description)
                    apply_fn(cursor)
                    cursor.execute(
                        "INSERT INTO schema_version (version, description) VALUES (?, ?);",
                        (version, description),
                    )
                    current_version = version

        logger.info("Database schema is up to date at version %d", current_version)
        return current_version
