"""Unit tests for newly added repository methods: segment updates and vocabulary editing."""

import pytest
from live_transcript.database.models import Session, TranscriptSegment, VocabularyEntry
from live_transcript.database.repositories import (
    SegmentRepository,
    SessionRepository,
    VocabularyRepository,
)


def test_segment_repository_update_methods(
    session_repo: SessionRepository,
    segment_repo: SegmentRepository,
):
    session = Session.create_new(title="Segment Update Test")
    session_repo.create(session)

    segment = TranscriptSegment(
        id="seg-orig",
        session_id=session.id,
        sequence_number=0,
        start_time=1.0,
        end_time=4.0,
        original_text="Initial segment text with misktake.",
    )
    segment_repo.add(segment)

    # 1. Test update_segment_text
    success = segment_repo.update_segment_text("seg-orig", "Corrected segment text without mistake.")
    assert success is True

    fetched = segment_repo.get_by_id("seg-orig")
    assert fetched is not None
    assert fetched.original_text == "Corrected segment text without mistake."

    # 2. Test full segment update
    fetched.original_text = "Updated text again."
    fetched.status = "final"
    success_update = segment_repo.update_segment(fetched)
    assert success_update is True
    assert segment_repo.get_by_id("seg-orig").original_text == "Updated text again."


def test_segment_repository_save_session_segments(
    session_repo: SessionRepository,
    segment_repo: SegmentRepository,
):
    session = Session.create_new(title="Batch Save Test")
    session_repo.create(session)

    # Add 2 segments initially
    for i in range(2):
        segment_repo.add(
            TranscriptSegment(
                id=f"seg-batch-{i}",
                session_id=session.id,
                sequence_number=i,
                start_time=float(i * 3),
                end_time=float((i + 1) * 3),
                original_text=f"Batch segment original {i}",
            )
        )

    assert len(segment_repo.get_by_session(session.id)) == 2

    # Save new list of 3 segments replacing previous ones
    new_segments = [
        TranscriptSegment(
            id=f"seg-new-{i}",
            session_id=session.id,
            sequence_number=i,
            start_time=float(i * 2),
            end_time=float((i + 1) * 2),
            original_text=f"Replaced segment content {i}",
        )
        for i in range(3)
    ]

    saved = segment_repo.save_session_segments(session.id, new_segments)
    assert saved is True

    updated_list = segment_repo.get_by_session(session.id)
    assert len(updated_list) == 3
    assert updated_list[0].original_text == "Replaced segment content 0"
    assert updated_list[2].original_text == "Replaced segment content 2"


def test_vocabulary_repository_get_by_id_and_update(vocab_repo: VocabularyRepository):
    entry = VocabularyEntry(
        id="vocab-1",
        source_session_id=None,
        word_or_phrase="inference",
        meaning="The process of deriving logical conclusions from premises known or assumed to be true.",
        original_sentence="Local model inference runs on the GPU or CPU.",
    )
    vocab_repo.add(entry)

    # Test get_by_id
    fetched = vocab_repo.get_by_id("vocab-1")
    assert fetched is not None
    assert fetched.word_or_phrase == "inference"

    # Test update
    fetched.meaning = "Updated definition: running trained neural network to make predictions."
    fetched.example_sentence = "Whisper performs inference locally."
    success = vocab_repo.update(fetched)
    assert success is True

    re_fetched = vocab_repo.get_by_id("vocab-1")
    assert re_fetched.meaning == "Updated definition: running trained neural network to make predictions."
    assert re_fetched.example_sentence == "Whisper performs inference locally."
