"""Editable and selectable transcript text editor widget with timestamp preservation."""

import re
from typing import List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QContextMenuEvent, QTextCursor
from PySide6.QtWidgets import QApplication, QMenu, QPlainTextEdit, QWidget

from live_transcript.database.models import TranscriptSegment, utc_now_iso
from live_transcript.utils.logging_setup import get_logger

logger = get_logger("ui.widgets.transcript_editor")


class TranscriptEditorWidget(QPlainTextEdit):
    """Editable and selectable transcript area with timestamp parsing and context actions."""

    lookup_requested = Signal(str, str)  # (selected_word, context_sentence)
    save_requested = Signal()
    selection_state_changed = Signal(bool)  # (has_selection)

    # Regex to parse [MM:SS - MM:SS] text
    TIMESTAMP_PATTERN = re.compile(
        r"^\[\s*(\d{1,3}):(\d{2})\s*-\s*(\d{1,3}):(\d{2})\s*\]\s*(.*)$"
    )

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._segments: List[TranscriptSegment] = []
        self._is_editing_locked: bool = False

        self.setPlaceholderText("Transcript will appear here in real time...")
        self.setStyleSheet(
            "font-family: 'Segoe UI', system-ui, sans-serif; "
            "font-size: 14px; line-height: 1.5; "
            "background-color: #0F172A; color: #F8FAFC; "
            "border: 1px solid #334155; border-radius: 8px; padding: 12px;"
        )

        # Enable text selection
        self.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextEditorInteraction
        )

        self.cursorPositionChanged.connect(self._on_cursor_changed)

    def _on_cursor_changed(self) -> None:
        has_sel = bool(self.textCursor().hasSelection())
        self.selection_state_changed.emit(has_sel)

    def set_segments(self, segments: List[TranscriptSegment]) -> None:
        """Populate the editor with transcript segments formatted with timestamps."""
        self._segments = list(segments)
        lines = []
        for seg in self._segments:
            start_m, start_s = divmod(int(seg.start_time), 60)
            end_m, end_s = divmod(int(seg.end_time), 60)
            lines.append(f"[{start_m:02d}:{start_s:02d} - {end_m:02d}:{end_s:02d}] {seg.original_text}")

        full_text = "\n".join(lines)
        self.setPlainText(full_text)
        self.document().setModified(False)

    def append_segment(self, segment: TranscriptSegment) -> None:
        """Append a newly transcribed segment to the editor."""
        self._segments.append(segment)
        start_m, start_s = divmod(int(segment.start_time), 60)
        end_m, end_s = divmod(int(segment.end_time), 60)
        new_line = f"[{start_m:02d}:{start_s:02d} - {end_m:02d}:{end_s:02d}] {segment.original_text}"

        cursor = self.textCursor()
        # Save position
        saved_pos = cursor.position()
        has_selection = cursor.hasSelection()
        is_at_end = cursor.atEnd()

        cursor.movePosition(QTextCursor.MoveOperation.End)
        if self.toPlainText().strip():
            cursor.insertText("\n" + new_line)
        else:
            cursor.insertText(new_line)

        # Restore cursor if user was selecting/editing elsewhere
        if not is_at_end and (has_selection or self.document().isModified()):
            cursor.setPosition(saved_pos)
            self.setTextCursor(cursor)
        else:
            self.moveCursor(QTextCursor.MoveOperation.End)

    def get_selected_text(self) -> str:
        """Return currently selected text."""
        return self.textCursor().selectedText().replace("\u2029", "\n").strip()

    def get_surrounding_sentence(self) -> str:
        """Extract the full line or sentence around the current selection/cursor."""
        cursor = self.textCursor()
        block = cursor.block()
        line_text = block.text().strip()
        # Remove timestamp prefix if present
        m = self.TIMESTAMP_PATTERN.match(line_text)
        if m:
            return m.group(5).strip()
        return line_text

    def copy_selected(self) -> bool:
        """Copy selected text to clipboard. Returns True if text was copied."""
        text = self.get_selected_text()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            return True
        return False

    def copy_all(self) -> None:
        """Copy complete transcript text to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.toPlainText().strip())

    def parse_edited_segments(self, session_id: str) -> List[TranscriptSegment]:
        """Parse the editor lines back into TranscriptSegment objects preserving timestamps."""
        raw_text = self.toPlainText().strip()
        if not raw_text:
            return []

        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        result_segments: List[TranscriptSegment] = []
        now = utc_now_iso()

        current_time = 0.0
        for idx, line in enumerate(lines, start=1):
            m = self.TIMESTAMP_PATTERN.match(line)
            if m:
                s_m, s_s, e_m, e_s, text = m.groups()
                start_sec = float(int(s_m) * 60 + int(s_s))
                end_sec = float(int(e_m) * 60 + int(e_s))
                current_time = end_sec
            else:
                # Line without timestamp: estimate from sequence
                start_sec = current_time
                end_sec = current_time + 3.0
                text = line
                current_time = end_sec

            # Try to preserve existing segment ID if index matches
            seg_id = None
            if idx - 1 < len(self._segments):
                seg_id = self._segments[idx - 1].id

            seg = TranscriptSegment(
                id=seg_id or TranscriptSegment.create_new(session_id, idx, start_sec, end_sec, text).id,
                session_id=session_id,
                sequence_number=idx,
                start_time=start_sec,
                end_time=end_sec,
                original_text=text.strip(),
                translated_text=None,
                detected_language="en",
                status="final",
                created_at=now,
                updated_at=now,
            )
            result_segments.append(seg)

        self._segments = result_segments
        self.document().setModified(False)
        return result_segments

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        """Custom context menu with Copy, Look Up Meaning, and Save actions."""
        menu = QMenu(self)

        has_selection = self.textCursor().hasSelection()
        selected_text = self.get_selected_text()

        action_copy = QAction("📋 Copy", self)
        action_copy.setShortcut("Ctrl+C")
        action_copy.setEnabled(has_selection)
        action_copy.triggered.connect(self.copy_selected)
        menu.addAction(action_copy)

        action_copy_all = QAction("📄 Copy All", self)
        action_copy_all.triggered.connect(self.copy_all)
        menu.addAction(action_copy_all)

        menu.addSeparator()

        action_lookup = QAction("📖 Look Up Meaning & Save to Vocabulary", self)
        action_lookup.setEnabled(bool(selected_text))
        action_lookup.triggered.connect(self._on_lookup_action)
        menu.addAction(action_lookup)

        menu.addSeparator()

        action_save = QAction("💾 Save Changes", self)
        action_save.triggered.connect(self.save_requested.emit)
        menu.addAction(action_save)

        action_select_all = QAction("Select All", self)
        action_select_all.setShortcut("Ctrl+A")
        action_select_all.triggered.connect(self.selectAll)
        menu.addAction(action_select_all)

        menu.exec(event.globalPos())

    def _on_lookup_action(self) -> None:
        """Trigger vocabulary lookup for the selected word or phrase."""
        selected_text = self.get_selected_text()
        if selected_text:
            context = self.get_surrounding_sentence()
            self.lookup_requested.emit(selected_text, context)
