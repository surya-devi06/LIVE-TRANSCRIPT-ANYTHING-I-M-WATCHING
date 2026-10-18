"""Data access repositories for Session, Segment, Vocabulary, and Settings."""

import sqlite3
from typing import List, Optional

from live_transcript.database.connection import DatabaseConnection
from live_transcript.database.models import (
    AppSettingRecord,
    Session,
    TranscriptSegment,
    VocabularyEntry,
    utc_now_iso,
)


class SessionRepository:
    """Repository for managing session persistence."""

    def __init__(self, db: DatabaseConnection) -> None:
        self.db = db

    def _row_to_session(self, row: sqlite3.Row) -> Session:
        return Session(
            id=row["id"],
            title=row["title"],
            started_at=row["started_at"],
            ended_at=row["ended_at"],
            duration_seconds=float(row["duration_seconds"]),
            source_type=row["source_type"],
            source_language=row["source_language"],
            target_language=row["target_language"],
            transcription_provider=row["transcription_provider"],
            model_name=row["model_name"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def create(self, session: Session) -> Session:
        """Insert a new session."""
        with self.db.transaction() as cursor:
            cursor.execute(
                """
                INSERT INTO sessions (
                    id, title, started_at, ended_at, duration_seconds,
                    source_type, source_language, target_language,
                    transcription_provider, model_name, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    session.id,
                    session.title,
                    session.started_at,
                    session.ended_at,
                    session.duration_seconds,
                    session.source_type,
                    session.source_language,
                    session.target_language,
                    session.transcription_provider,
                    session.model_name,
                    session.created_at,
                    session.updated_at,
                ),
            )
        return session

    def get_by_id(self, session_id: str) -> Optional[Session]:
        """Fetch session by ID."""
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE id = ?;", (session_id,))
            row = cursor.fetchone()
            return self._row_to_session(row) if row else None

    def list_recent(self, limit: int = 50, offset: int = 0) -> List[Session]:
        """List sessions ordered by creation date descending."""
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM sessions
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?;
                """,
                (limit, offset),
            )
            return [self._row_to_session(r) for r in cursor.fetchall()]

    def search(self, query: str, limit: int = 50) -> List[Session]:
        """Search sessions by title."""
        pattern = f"%{query}%"
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM sessions
                WHERE title LIKE ?
                ORDER BY created_at DESC
                LIMIT ?;
                """,
                (pattern, limit),
            )
            return [self._row_to_session(r) for r in cursor.fetchall()]

    def update(self, session: Session) -> None:
        """Update an existing session."""
        session.updated_at = utc_now_iso()
        with self.db.transaction() as cursor:
            cursor.execute(
                """
                UPDATE sessions SET
                    title = ?,
                    ended_at = ?,
                    duration_seconds = ?,
                    source_type = ?,
                    source_language = ?,
                    target_language = ?,
                    transcription_provider = ?,
                    model_name = ?,
                    updated_at = ?
                WHERE id = ?;
                """,
                (
                    session.title,
                    session.ended_at,
                    session.duration_seconds,
                    session.source_type,
                    session.source_language,
                    session.target_language,
                    session.transcription_provider,
                    session.model_name,
                    session.updated_at,
                    session.id,
                ),
            )

    def delete(self, session_id: str) -> bool:
        """Delete a session (cascades to segments)."""
        with self.db.transaction() as cursor:
            cursor.execute("DELETE FROM sessions WHERE id = ?;", (session_id,))
            return cursor.rowcount > 0

    def count(self) -> int:
        """Return total number of saved sessions."""
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sessions;")
            return int(cursor.fetchone()[0])


class SegmentRepository:
    """Repository for managing transcript segment persistence."""

    def __init__(self, db: DatabaseConnection) -> None:
        self.db = db

    def _row_to_segment(self, row: sqlite3.Row) -> TranscriptSegment:
        return TranscriptSegment(
            id=row["id"],
            session_id=row["session_id"],
            sequence_number=int(row["sequence_number"]),
            start_time=float(row["start_time"]),
            end_time=float(row["end_time"]),
            original_text=row["original_text"],
            translated_text=row["translated_text"],
            detected_language=row["detected_language"],
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def add(self, segment: TranscriptSegment) -> TranscriptSegment:
        """Insert a new transcript segment."""
        with self.db.transaction() as cursor:
            cursor.execute(
                """
                INSERT INTO transcript_segments (
                    id, session_id, sequence_number, start_time, end_time,
                    original_text, translated_text, detected_language,
                    status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    segment.id,
                    segment.session_id,
                    segment.sequence_number,
                    segment.start_time,
                    segment.end_time,
                    segment.original_text,
                    segment.translated_text,
                    segment.detected_language,
                    segment.status,
                    segment.created_at,
                    segment.updated_at,
                ),
            )
        return segment

    def get_by_session(self, session_id: str) -> List[TranscriptSegment]:
        """Fetch all segments for a session ordered by sequence number."""
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM transcript_segments
                WHERE session_id = ?
                ORDER BY sequence_number ASC;
                """,
                (session_id,),
            )
            return [self._row_to_segment(r) for r in cursor.fetchall()]

    def count_for_session(self, session_id: str) -> int:
        """Return total segments in a session."""
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM transcript_segments WHERE session_id = ?;",
                (session_id,),
            )
            return int(cursor.fetchone()[0])

    def get_latest_sequence_number(self, session_id: str) -> int:
        """Get the highest sequence number for a session, or 0 if none exist."""
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COALESCE(MAX(sequence_number), 0) FROM transcript_segments WHERE session_id = ?;",
                (session_id,),
            )
            row = cursor.fetchone()
            return int(row[0]) if row else 0

    def update_translation(self, segment_id: str, translated_text: str) -> None:
        """Associate translated text with an existing segment."""
        with self.db.transaction() as cursor:
            cursor.execute(
                """
                UPDATE transcript_segments
                SET translated_text = ?, updated_at = ?
                WHERE id = ?;
                """,
                (translated_text, utc_now_iso(), segment_id),
            )

    def search(self, session_id: str, query: str) -> List[TranscriptSegment]:
        """Search segments in a session by text content."""
        pattern = f"%{query}%"
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM transcript_segments
                WHERE session_id = ? AND (original_text LIKE ? OR translated_text LIKE ?)
                ORDER BY sequence_number ASC;
                """,
                (session_id, pattern, pattern),
            )
            return [self._row_to_segment(r) for r in cursor.fetchall()]

    def update_segment_text(self, segment_id: str, original_text: str) -> bool:
        """Update original text for a segment."""
        now = utc_now_iso()
        with self.db.transaction() as cursor:
            cursor.execute(
                """
                UPDATE transcript_segments
                SET original_text = ?, updated_at = ?
                WHERE id = ?;
                """,
                (original_text, now, segment_id),
            )
            return cursor.rowcount > 0

    def update_segment(self, segment: TranscriptSegment) -> bool:
        """Update full segment record."""
        segment.updated_at = utc_now_iso()
        with self.db.transaction() as cursor:
            cursor.execute(
                """
                UPDATE transcript_segments
                SET sequence_number = ?, start_time = ?, end_time = ?,
                    original_text = ?, translated_text = ?, detected_language = ?,
                    status = ?, updated_at = ?
                WHERE id = ?;
                """,
                (
                    segment.sequence_number,
                    segment.start_time,
                    segment.end_time,
                    segment.original_text,
                    segment.translated_text,
                    segment.detected_language,
                    segment.status,
                    segment.updated_at,
                    segment.id,
                ),
            )
            return cursor.rowcount > 0

    def get_by_id(self, segment_id: str) -> Optional[TranscriptSegment]:
        """Fetch a single segment by its ID."""
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transcript_segments WHERE id = ?;", (segment_id,))
            row = cursor.fetchone()
            return self._row_to_segment(row) if row else None

    def save_session_segments(self, session_id: str, segments: List[TranscriptSegment]) -> bool:
        """Persist or update all segments for a session in a single transaction."""
        now = utc_now_iso()
        with self.db.transaction() as cursor:
            cursor.execute("DELETE FROM transcript_segments WHERE session_id = ?;", (session_id,))
            for idx, seg in enumerate(segments, start=1):
                seg.sequence_number = idx
                if not seg.session_id:
                    seg.session_id = session_id
                if not seg.created_at:
                    seg.created_at = now
                seg.updated_at = now
                cursor.execute(
                    """
                    INSERT INTO transcript_segments (
                        id, session_id, sequence_number, start_time, end_time,
                        original_text, translated_text, detected_language,
                        status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        seg.id,
                        session_id,
                        seg.sequence_number,
                        seg.start_time,
                        seg.end_time,
                        seg.original_text,
                        seg.translated_text,
                        seg.detected_language,
                        seg.status,
                        seg.created_at,
                        seg.updated_at,
                    ),
                )
        return True


class VocabularyRepository:
    """Repository for managing saved vocabulary entries."""

    def __init__(self, db: DatabaseConnection) -> None:
        self.db = db

    def _row_to_entry(self, row: sqlite3.Row) -> VocabularyEntry:
        return VocabularyEntry(
            id=row["id"],
            word_or_phrase=row["word_or_phrase"],
            original_sentence=row["original_sentence"],
            meaning=row["meaning"],
            example_sentence=row["example_sentence"] or "",
            explanation_language=row["explanation_language"],
            source_session_id=row["source_session_id"],
            created_at=row["created_at"],
        )

    def add(self, entry: VocabularyEntry) -> VocabularyEntry:
        """Insert a vocabulary entry."""
        with self.db.transaction() as cursor:
            cursor.execute(
                """
                INSERT INTO vocabulary_entries (
                    id, word_or_phrase, original_sentence, meaning,
                    example_sentence, explanation_language,
                    source_session_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    entry.id,
                    entry.word_or_phrase,
                    entry.original_sentence,
                    entry.meaning,
                    entry.example_sentence,
                    entry.explanation_language,
                    entry.source_session_id,
                    entry.created_at,
                ),
            )
        return entry

    def list_all(self, limit: int = 100, offset: int = 0) -> List[VocabularyEntry]:
        """List all vocabulary entries ordered by newest first."""
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM vocabulary_entries
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?;
                """,
                (limit, offset),
            )
            return [self._row_to_entry(r) for r in cursor.fetchall()]

    def search(self, query: str) -> List[VocabularyEntry]:
        """Search vocabulary by word or meaning."""
        pattern = f"%{query}%"
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM vocabulary_entries
                WHERE word_or_phrase LIKE ? OR meaning LIKE ?
                ORDER BY created_at DESC;
                """,
                (pattern, pattern),
            )
            return [self._row_to_entry(r) for r in cursor.fetchall()]

    def get_by_id(self, entry_id: str) -> Optional[VocabularyEntry]:
        """Fetch a single vocabulary entry by ID."""
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM vocabulary_entries WHERE id = ?;", (entry_id,))
            row = cursor.fetchone()
            return self._row_to_entry(row) if row else None

    def update(self, entry: VocabularyEntry) -> bool:
        """Update an existing vocabulary entry."""
        with self.db.transaction() as cursor:
            cursor.execute(
                """
                UPDATE vocabulary_entries SET
                    word_or_phrase = ?,
                    original_sentence = ?,
                    meaning = ?,
                    example_sentence = ?,
                    explanation_language = ?
                WHERE id = ?;
                """,
                (
                    entry.word_or_phrase,
                    entry.original_sentence,
                    entry.meaning,
                    entry.example_sentence,
                    entry.explanation_language,
                    entry.id,
                ),
            )
            return cursor.rowcount > 0

    def delete(self, entry_id: str) -> bool:
        """Delete a vocabulary entry."""
        with self.db.transaction() as cursor:
            cursor.execute("DELETE FROM vocabulary_entries WHERE id = ?;", (entry_id,))
            return cursor.rowcount > 0

    def count(self) -> int:
        """Return total number of saved vocabulary entries."""
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM vocabulary_entries;")
            return int(cursor.fetchone()[0])


class SettingsRepository:
    """Repository for persisting key-value application settings in SQLite."""

    def __init__(self, db: DatabaseConnection) -> None:
        self.db = db

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieve setting value by key."""
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM app_settings WHERE key = ?;", (key,))
            row = cursor.fetchone()
            return str(row["value"]) if row else default

    def set(self, key: str, value: str) -> None:
        """Upsert setting key and value."""
        now = utc_now_iso()
        with self.db.transaction() as cursor:
            cursor.execute(
                """
                INSERT INTO app_settings (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at;
                """,
                (key, str(value), now),
            )

    def get_all(self) -> dict[str, str]:
        """Fetch all stored key-value settings as a dictionary."""
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM app_settings;")
            return {row["key"]: row["value"] for row in cursor.fetchall()}

    def delete(self, key: str) -> bool:
        """Remove a setting key."""
        with self.db.transaction() as cursor:
            cursor.execute("DELETE FROM app_settings WHERE key = ?;", (key,))
            return cursor.rowcount > 0
