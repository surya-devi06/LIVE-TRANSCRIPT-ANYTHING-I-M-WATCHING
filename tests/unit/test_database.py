"""Unit tests for SQLite database connection, migrations, and repositories."""

from live_transcript.database.connection import DatabaseConnection
from live_transcript.database.migrations import MigrationRunner
from live_transcript.database.models import (
    Session,
    TranscriptSegment,
    VocabularyEntry,
)
from live_transcript.database.repositories import (
    SegmentRepository,
    SessionRepository,
    SettingsRepository,
    VocabularyRepository,
)


def test_migrations_runner(temp_data_dir) -> None:
    """Test that migrations initialize cleanly and idempotently."""
    db = DatabaseConnection(temp_data_dir / "migration_test.db")
    runner = MigrationRunner(db)

    # Initial migration run
    version1 = runner.run_migrations()
    assert version1 == 1
    assert runner.get_current_version() == 1

    # Second run should be a no-op
    version2 = runner.run_migrations()
    assert version2 == 1


def test_session_repository_crud(session_repo: SessionRepository) -> None:
    """Verify session creation, retrieval, update, search, and deletion."""
    session = Session.create_new(
        title="Python Tutorial Live",
        source_language="en",
        target_language="ta",
        model_name="base",
    )

    # Create
    created = session_repo.create(session)
    assert created.id == session.id

    # Get by ID
    fetched = session_repo.get_by_id(session.id)
    assert fetched is not None
    assert fetched.title == "Python Tutorial Live"
    assert fetched.target_language == "ta"

    # Search
    results = session_repo.search("Tutorial")
    assert len(results) == 1
    assert results[0].id == session.id

    # Update
    fetched.title = "Python Tutorial Live (Completed)"
    fetched.duration_seconds = 125.5
    session_repo.update(fetched)

    updated = session_repo.get_by_id(session.id)
    assert updated.title == "Python Tutorial Live (Completed)"
    assert updated.duration_seconds == 125.5

    # Delete
    assert session_repo.delete(session.id) is True
    assert session_repo.get_by_id(session.id) is None


def test_segment_repository_and_foreign_key_cascade(
    test_db: DatabaseConnection,
    session_repo: SessionRepository,
    segment_repo: SegmentRepository,
) -> None:
    """Verify segment operations and foreign key CASCADE delete."""
    session = session_repo.create(Session.create_new(title="Cascade Test"))

    seg1 = segment_repo.add(
        TranscriptSegment.create_new(
            session_id=session.id,
            sequence_number=1,
            start_time=0.0,
            end_time=3.5,
            original_text="Welcome to the live stream.",
            detected_language="en",
        )
    )

    seg2 = segment_repo.add(
        TranscriptSegment.create_new(
            session_id=session.id,
            sequence_number=2,
            start_time=3.5,
            end_time=7.0,
            original_text="Today we learn full-stack development.",
            detected_language="en",
        )
    )

    # Fetch ordered segments
    segments = segment_repo.get_by_session(session.id)
    assert len(segments) == 2
    assert segments[0].sequence_number == 1
    assert segments[1].sequence_number == 2
    assert segment_repo.count_for_session(session.id) == 2
    assert segment_repo.get_latest_sequence_number(session.id) == 2

    # Update translation
    segment_repo.update_translation(seg1.id, "நேரலை ஸ்ட்ரீமுக்கு வரவேற்கிறோம்.")
    updated_segs = segment_repo.get_by_session(session.id)
    assert updated_segs[0].translated_text == "நேரலை ஸ்ட்ரீமுக்கு வரவேற்கிறோம்."

    # Search within session
    matches = segment_repo.search(session.id, "development")
    assert len(matches) == 1
    assert matches[0].id == seg2.id

    # Cascade delete verification
    session_repo.delete(session.id)
    assert segment_repo.count_for_session(session.id) == 0


def test_vocabulary_repository(vocab_repo: VocabularyRepository) -> None:
    """Verify saving, searching, and deleting vocabulary entries."""
    entry = vocab_repo.add(
        VocabularyEntry.create_new(
            word_or_phrase="concurrent",
            original_sentence="The system handles concurrent audio loops.",
            meaning="occurring or existing at the same time",
            example_sentence="There are multiple concurrent workers.",
        )
    )

    assert entry.id is not None
    assert vocab_repo.count() == 1

    # Search
    search_res = vocab_repo.search("concurrent")
    assert len(search_res) == 1
    assert search_res[0].word_or_phrase == "concurrent"

    # Delete
    assert vocab_repo.delete(entry.id) is True
    assert vocab_repo.count() == 0


def test_settings_repository(settings_repo: SettingsRepository) -> None:
    """Verify key-value settings persistence and updates."""
    settings_repo.set("theme", "dark")
    settings_repo.set("model_name", "small")

    assert settings_repo.get("theme") == "dark"
    assert settings_repo.get("model_name") == "small"
    assert settings_repo.get("missing_key", default="default_val") == "default_val"

    # Update key
    settings_repo.set("theme", "light")
    assert settings_repo.get("theme") == "light"

    all_settings = settings_repo.get_all()
    assert all_settings["theme"] == "light"
    assert all_settings["model_name"] == "small"

    # Delete
    assert settings_repo.delete("model_name") is True
    assert settings_repo.get("model_name") is None
