"""Unit and integration tests for HistoryView and VocabularyView workflows."""

import pytest
from PySide6.QtWidgets import QApplication

from live_transcript.database.models import Session, TranscriptSegment, VocabularyEntry
from live_transcript.database.repositories import (
    SegmentRepository,
    SessionRepository,
    VocabularyRepository,
)
from live_transcript.ui.views.history_view import HistoryView
from live_transcript.ui.views.vocabulary_view import VocabularyView


def test_history_view_open_session_and_save_edits(
    qtbot,
    session_repo: SessionRepository,
    segment_repo: SegmentRepository,
    vocab_repo: VocabularyRepository,
):
    # 1. Setup session and segments
    session = Session.create_new(title="Lecture on Neural Networks")
    session_repo.create(session)

    segment = TranscriptSegment(
        id="seg-h1",
        session_id=session.id,
        sequence_number=0,
        start_time=0.0,
        end_time=4.0,
        original_text="Deep learning models learn feature representations automatically.",
    )
    segment_repo.add(segment)

    # 2. Instantiate HistoryView
    view = HistoryView(session_repo, segment_repo, vocab_repo)
    qtbot.addWidget(view)
    view.refresh()

    # Initial state should show the sessions table (page 0)
    assert view.stack.currentIndex() == 0
    assert view.table.rowCount() == 1

    # 3. Open the session
    view.open_session(session.id)
    assert view.stack.currentIndex() == 1  # detail view
    assert view.input_session_title.text() == "Lecture on Neural Networks"
    assert "Deep learning models learn feature representations" in view.transcript_editor.toPlainText()

    # 4. Modify transcript text and save
    view.transcript_editor.setPlainText("[00:00 - 00:04] Deep learning models learn robust feature representations automatically.")
    view._save_changes()

    # Verify changes were persisted in SQLite
    updated_segs = segment_repo.get_by_session(session.id)
    assert len(updated_segs) == 1
    assert "robust feature representations" in updated_segs[0].original_text

    # 5. Back to list
    view.close_detail_view()
    assert view.stack.currentIndex() == 0


def test_vocabulary_view_table_and_search(
    qtbot,
    vocab_repo: VocabularyRepository,
):
    # Setup entries
    vocab_repo.add(
        VocabularyEntry(
            id="v-1",
            word_or_phrase="acoustic",
            meaning="Relating to sound or the sense of hearing.",
            original_sentence="The acoustic model recognizes phonemes from sound waves.",
        )
    )
    vocab_repo.add(
        VocabularyEntry(
            id="v-2",
            word_or_phrase="latency",
            meaning="The delay before a transfer of data begins following an instruction.",
            original_sentence="Real-time applications require low latency transcription.",
        )
    )

    view = VocabularyView(vocab_repo)
    qtbot.addWidget(view)
    view.refresh()

    assert view.table.rowCount() == 2

    # Search filter
    view.search_input.setText("latency")
    assert view.table.rowCount() == 1
    assert view.table.item(0, 0).text() == "latency"

    view.search_input.setText("")
    assert view.table.rowCount() == 2
