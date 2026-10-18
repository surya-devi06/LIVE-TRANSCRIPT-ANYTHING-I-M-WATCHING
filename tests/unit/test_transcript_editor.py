"""Unit tests for TranscriptEditorWidget formatting, selection, and parsing."""

import pytest
from PySide6.QtWidgets import QApplication

from live_transcript.database.models import TranscriptSegment
from live_transcript.ui.widgets.transcript_editor import TranscriptEditorWidget


@pytest.fixture
def sample_segments():
    return [
        TranscriptSegment(
            id="seg-1",
            session_id="sess-1",
            sequence_number=0,
            start_time=0.0,
            end_time=3.5,
            original_text="Welcome to the live transcription test.",
        ),
        TranscriptSegment(
            id="seg-2",
            session_id="sess-1",
            sequence_number=1,
            start_time=3.5,
            end_time=7.2,
            original_text="Speech recognition processes audio streams locally.",
        ),
    ]


def test_transcript_editor_set_and_append_segments(qtbot, sample_segments):
    widget = TranscriptEditorWidget()
    qtbot.addWidget(widget)

    # Set initial segments
    widget.set_segments(sample_segments)
    text = widget.toPlainText()
    assert "[00:00 - 00:03] Welcome to the live transcription test." in text
    assert "[00:03 - 00:07] Speech recognition processes audio streams locally." in text

    # Append new segment
    new_segment = TranscriptSegment(
        id="seg-3",
        session_id="sess-1",
        sequence_number=2,
        start_time=7.2,
        end_time=10.0,
        original_text="This third sentence was appended in real time.",
    )
    widget.append_segment(new_segment)
    updated_text = widget.toPlainText()
    assert "[00:07 - 00:10] This third sentence was appended in real time." in updated_text


def test_transcript_editor_parse_segments(qtbot, sample_segments):
    widget = TranscriptEditorWidget()
    qtbot.addWidget(widget)
    widget.set_segments(sample_segments)

    # Edit the text manually
    widget.setPlainText(
        "[00:00 - 00:03] Welcome to the EDITED transcription test.\n"
        "[00:03 - 00:07] Speech recognition processes audio streams accurately."
    )

    parsed = widget.parse_edited_segments("sess-1")
    assert len(parsed) == 2
    assert parsed[0].original_text == "Welcome to the EDITED transcription test."
    assert parsed[0].start_time == 0.0
    assert parsed[0].end_time == 3.0
    assert parsed[1].original_text == "Speech recognition processes audio streams accurately."
    assert parsed[1].start_time == 3.0
    assert parsed[1].end_time == 7.0


def test_transcript_editor_copy_actions(qtbot, sample_segments):
    widget = TranscriptEditorWidget()
    qtbot.addWidget(widget)
    widget.set_segments(sample_segments)

    # Copy All executes without error
    widget.copy_all()
    assert "[00:00 - 00:03] Welcome to the live transcription test." in widget.toPlainText()

    # Select and test get_selected_text
    start_idx = widget.toPlainText().find("Welcome")
    cursor = widget.textCursor()
    cursor.setPosition(start_idx)
    cursor.setPosition(start_idx + len("Welcome"), cursor.MoveMode.KeepAnchor)
    widget.setTextCursor(cursor)

    assert widget.get_selected_text() == "Welcome"
    copied = widget.copy_selected()
    assert copied is True


def test_transcript_editor_word_and_context_extraction(qtbot, sample_segments):
    widget = TranscriptEditorWidget()
    qtbot.addWidget(widget)
    widget.set_segments(sample_segments)

    # Select the word "recognition"
    text = widget.toPlainText()
    start_idx = text.find("recognition")
    cursor = widget.textCursor()
    cursor.setPosition(start_idx)
    cursor.setPosition(start_idx + len("recognition"), cursor.MoveMode.KeepAnchor)
    widget.setTextCursor(cursor)

    word = widget.get_selected_text()
    context = widget.get_surrounding_sentence()
    assert word == "recognition"
    assert "Speech recognition processes audio streams locally" in context
