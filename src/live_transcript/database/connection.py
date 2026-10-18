"""SQLite connection provider and context manager."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Union

from live_transcript.utils.logging_setup import get_logger

logger = get_logger("database.connection")


class DatabaseConnection:
    """Manages SQLite database connections with foreign keys and WAL mode."""

    def __init__(self, db_path: Union[str, Path]) -> None:
        self.db_path = str(db_path)

    def get_connection(self) -> sqlite3.Connection:
        """Create and configure a new SQLite connection."""
        conn = sqlite3.connect(
            self.db_path,
            timeout=10.0,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )
        conn.row_factory = sqlite3.Row

        # Performance and integrity pragmas
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("PRAGMA journal_mode = WAL;")
        cursor.execute("PRAGMA busy_timeout = 5000;")
        cursor.execute("PRAGMA synchronous = NORMAL;")
        cursor.close()

        return conn

    @contextmanager
    def connect(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for obtaining an auto-closing database connection."""
        conn = self.get_connection()
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Cursor, None, None]:
        """Context manager for executing an atomic transaction."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
