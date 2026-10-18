"""Data models representing database entities."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
import uuid


def utc_now_iso() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def new_id() -> str:
    """Generate a standard UUID4 hex string."""
    return uuid.uuid4().hex


@dataclass
class Session:
    """Represents a transcription session."""
    id: str
    title: str
    started_at: str
    ended_at: Optional[str] = None
    duration_seconds: float = 0.0
    source_type: str = "System Audio"
    source_language: str = "auto"
    target_language: str = "en"
    transcription_provider: str = "local_whisper"
    model_name: str = "base"
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def create_new(
        cls,
        title: str = "Untitled Session",
        source_type: str = "System Audio",
        source_language: str = "auto",
        target_language: str = "en",
        transcription_provider: str = "local_whisper",
        model_name: str = "base",
    ) -> "Session":
        now = utc_now_iso()
        return cls(
            id=new_id(),
            title=title,
            started_at=now,
            ended_at=None,
            duration_seconds=0.0,
            source_type=source_type,
            source_language=source_language,
            target_language=target_language,
            transcription_provider=transcription_provider,
            model_name=model_name,
            created_at=now,
            updated_at=now,
        )


@dataclass
class TranscriptSegment:
    """Represents an individual chunk/segment of recognized speech."""
    id: str
    session_id: str
    sequence_number: int
    start_time: float
    end_time: float
    original_text: str
    translated_text: Optional[str] = None
    detected_language: Optional[str] = None
    status: str = "final"
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def create_new(
        cls,
        session_id: str,
        sequence_number: int,
        start_time: float,
        end_time: float,
        original_text: str,
        translated_text: Optional[str] = None,
        detected_language: Optional[str] = None,
        status: str = "final",
    ) -> "TranscriptSegment":
        now = utc_now_iso()
        return cls(
            id=new_id(),
            session_id=session_id,
            sequence_number=sequence_number,
            start_time=start_time,
            end_time=end_time,
            original_text=original_text,
            translated_text=translated_text,
            detected_language=detected_language,
            status=status,
            created_at=now,
            updated_at=now,
        )


@dataclass
class VocabularyEntry:
    """Represents a saved word or phrase for language learning."""
    id: str
    word_or_phrase: str
    original_sentence: str
    meaning: str
    example_sentence: str = ""
    explanation_language: str = "en"
    source_session_id: Optional[str] = None
    created_at: str = ""

    @classmethod
    def create_new(
        cls,
        word_or_phrase: str,
        original_sentence: str,
        meaning: str,
        example_sentence: str = "",
        explanation_language: str = "en",
        source_session_id: Optional[str] = None,
    ) -> "VocabularyEntry":
        now = utc_now_iso()
        return cls(
            id=new_id(),
            word_or_phrase=word_or_phrase,
            original_sentence=original_sentence,
            meaning=meaning,
            example_sentence=example_sentence,
            explanation_language=explanation_language,
            source_session_id=source_session_id,
            created_at=now,
        )


@dataclass
class AppSettingRecord:
    """Represents a persisted key-value setting."""
    key: str
    value: str
    updated_at: str
