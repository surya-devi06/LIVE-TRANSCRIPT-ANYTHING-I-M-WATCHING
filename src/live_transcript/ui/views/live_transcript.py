"""Live transcript screen with capture controls, text selection, editing, and vocabulary integration."""

from typing import List, Optional
from PySide6.QtCore import QTime, QTimer, Qt, Signal
from PySide6.QtGui import QAction, QContextMenuEvent
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from live_transcript.constants import AppState, AudioSourceType, DisplayMode
from live_transcript.database.models import TranscriptSegment
from live_transcript.database.repositories import SegmentRepository, VocabularyRepository
from live_transcript.ui.dialogs.word_lookup_dialog import WordLookupDialog
from live_transcript.ui.widgets.audio_meter import AudioLevelMeter
from live_transcript.ui.widgets.transcript_editor import TranscriptEditorWidget
from live_transcript.utils.logging_setup import get_logger

logger = get_logger("ui.views.live_transcript")


class SegmentCard(QFrame):
    """Widget displaying a single transcript segment with selectable and editable text."""

    lookup_requested = Signal(str, str)   # (selected_text, context_sentence)
    edit_saved = Signal(str, str)         # (segment_id, new_text)

    def __init__(
        self,
        segment: TranscriptSegment,
        display_mode: DisplayMode = DisplayMode.ORIGINAL_ONLY,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.segment = segment
        self.display_mode = display_mode

        self.setProperty("class", "card")
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Header: Timestamp, Sequence Badge, and Actions
        header_layout = QHBoxLayout()
        start_m, start_s = divmod(int(self.segment.start_time), 60)
        end_m, end_s = divmod(int(self.segment.end_time), 60)
        lbl_time = QLabel(f"[{start_m:02d}:{start_s:02d} - {end_m:02d}:{end_s:02d}]", self)
        lbl_time.setStyleSheet("color: #38BDF8; font-weight: 600; font-size: 11px;")
        header_layout.addWidget(lbl_time)

        if self.segment.detected_language:
            lbl_lang = QLabel(self.segment.detected_language.upper(), self)
            lbl_lang.setStyleSheet(
                "background-color: #2D3139; color: #94A3B8; font-size: 10px; padding: 2px 6px; border-radius: 4px;"
            )
            header_layout.addWidget(lbl_lang)

        header_layout.addStretch()

        # Inline Quick Edit Button
        btn_edit = QPushButton("✏️ Edit", self)
        btn_edit.setStyleSheet(
            "padding: 2px 8px; font-size: 11px; background-color: #1E293B; color: #94A3B8; border-radius: 4px;"
        )
        btn_edit.clicked.connect(self._open_edit_dialog)
        header_layout.addWidget(btn_edit)

        layout.addLayout(header_layout)

        # Original text (selectable via mouse and keyboard)
        self.lbl_orig = QLabel(self.segment.original_text, self)
        self.lbl_orig.setWordWrap(True)
        self.lbl_orig.setStyleSheet("font-size: 14px; color: #F8FAFC; line-height: 1.4;")
        self.lbl_orig.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        layout.addWidget(self.lbl_orig)

        # Translated text (if present & mode requires it)
        self.lbl_trans = QLabel(self.segment.translated_text or "", self)
        self.lbl_trans.setWordWrap(True)
        self.lbl_trans.setStyleSheet("font-size: 13px; color: #A78BFA; font-style: italic;")
        self.lbl_trans.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )

        has_trans = bool(self.segment.translated_text)
        if self.display_mode == DisplayMode.TRANSLATION_ONLY and has_trans:
            self.lbl_orig.setVisible(False)
            self.lbl_trans.setVisible(True)
        elif self.display_mode == DisplayMode.BOTH and has_trans:
            self.lbl_orig.setVisible(True)
            self.lbl_trans.setVisible(True)
        else:
            self.lbl_trans.setVisible(False)

        layout.addWidget(self.lbl_trans)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        """Context menu on segment card allowing copying, editing, and vocabulary lookup."""
        menu = QMenu(self)

        selected_text = ""
        if self.lbl_orig.hasSelectedText():
            selected_text = self.lbl_orig.selectedText()
        elif self.lbl_trans.hasSelectedText():
            selected_text = self.lbl_trans.selectedText()

        action_copy = QAction("📋 Copy", self)
        action_copy.triggered.connect(lambda: QApplication.clipboard().setText(selected_text or self.segment.original_text))
        menu.addAction(action_copy)

        action_lookup = QAction("📖 Look Up Meaning & Save to Vocabulary", self)
        lookup_word = selected_text or self.segment.original_text
        action_lookup.triggered.connect(lambda: self.lookup_requested.emit(lookup_word, self.segment.original_text))
        menu.addAction(action_lookup)

        menu.addSeparator()

        action_edit = QAction("✏️ Edit Segment Text", self)
        action_edit.triggered.connect(self._open_edit_dialog)
        menu.addAction(action_edit)

        menu.exec(event.globalPos())

    def _open_edit_dialog(self) -> None:
        """Open a dialog to edit this segment's text."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Transcript Segment")
        dialog.setMinimumWidth(400)
        d_layout = QVBoxLayout(dialog)

        lbl = QLabel(f"Edit text for segment #{self.segment.sequence_number}:", dialog)
        d_layout.addWidget(lbl)

        txt_edit = QPlainTextEdit(self.segment.original_text, dialog)
        d_layout.addWidget(txt_edit)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, dialog)
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)
        d_layout.addWidget(btn_box)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_text = txt_edit.toPlainText().strip()
            if new_text and new_text != self.segment.original_text:
                self.segment.original_text = new_text
                self.lbl_orig.setText(new_text)
                self.edit_saved.emit(self.segment.id, new_text)


class LiveTranscriptView(QWidget):
    """View managing the live transcription stream, controls, selectable/editable view, and vocabulary."""

    start_clicked = Signal()
    pause_clicked = Signal()
    stop_clicked = Signal()
    clear_clicked = Signal()
    source_changed = Signal(AudioSourceType)
    device_changed = Signal(str, AudioSourceType)
    vocabulary_added = Signal(object)  # (VocabularyEntry)

    def __init__(
        self,
        segment_repo: Optional[SegmentRepository] = None,
        vocab_repo: Optional[VocabularyRepository] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.segment_repo = segment_repo
        self.vocab_repo = vocab_repo

        self._is_running = False
        self._is_paused = False
        self._elapsed_seconds = 0
        self._display_mode = DisplayMode.ORIGINAL_ONLY
        self._auto_scroll = True
        self._segments: List[TranscriptSegment] = []
        self._cards: List[SegmentCard] = []
        self.active_session_id: Optional[str] = None

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._on_timer_tick)

        self._setup_ui()

    def set_repositories(self, segment_repo: SegmentRepository, vocab_repo: VocabularyRepository) -> None:
        """Configure database repositories."""
        self.segment_repo = segment_repo
        self.vocab_repo = vocab_repo

    def set_session_id(self, session_id: str) -> None:
        """Set the active session ID."""
        self.active_session_id = session_id

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # 1. Top Control Bar
        control_bar = QFrame(self)
        control_bar.setProperty("class", "card")
        cb_layout = QHBoxLayout(control_bar)
        cb_layout.setContentsMargins(12, 10, 12, 10)
        cb_layout.setSpacing(12)

        # Start / Stop / Pause buttons
        self.btn_start = QPushButton("▶  Start", control_bar)
        self.btn_start.setProperty("class", "primary-btn")
        self.btn_start.clicked.connect(self._handle_start)

        self.btn_pause = QPushButton("⏸  Pause", control_bar)
        self.btn_pause.setEnabled(False)
        self.btn_pause.clicked.connect(self._handle_pause)

        self.btn_stop = QPushButton("⏹  Stop", control_bar)
        self.btn_stop.setProperty("class", "danger-btn")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self._handle_stop)

        cb_layout.addWidget(self.btn_start)
        cb_layout.addWidget(self.btn_pause)
        cb_layout.addWidget(self.btn_stop)

        # Audio Device / Source Selector
        lbl_source = QLabel("Device:", control_bar)
        lbl_source.setStyleSheet("color: #94A3B8; font-weight: 500;")
        self.combo_source = QComboBox(control_bar)
        self.combo_source.setMinimumWidth(220)
        self.combo_source.addItem("Default System Audio (Loopback)", ("", AudioSourceType.SYSTEM_LOOPBACK))
        self.combo_source.currentIndexChanged.connect(self._on_device_selection_changed)

        cb_layout.addWidget(lbl_source)
        cb_layout.addWidget(self.combo_source)

        # Live Audio Level Meter
        cb_layout.addSpacing(6)
        self.audio_meter = AudioLevelMeter(control_bar)
        cb_layout.addWidget(self.audio_meter)

        # Session Timer
        cb_layout.addStretch()
        self.lbl_timer = QLabel("00:00:00", control_bar)
        self.lbl_timer.setStyleSheet("font-family: monospace; font-size: 14px; font-weight: 700; color: #38BDF8;")
        cb_layout.addWidget(self.lbl_timer)

        layout.addWidget(control_bar)

        # 2. Filter, Actions, and View Options Toolbar
        tool_bar = QHBoxLayout()
        tool_bar.setSpacing(10)

        # Search box
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("🔍  Search in transcript...")
        self.search_input.textChanged.connect(self._filter_segments)
        tool_bar.addWidget(self.search_input, stretch=1)

        # Copy Selected Button
        self.btn_copy_selected = QPushButton("📋 Copy", self)
        self.btn_copy_selected.setToolTip("Copy selected text (or entire transcript if none selected)")
        self.btn_copy_selected.clicked.connect(self._copy_selected_or_all)
        tool_bar.addWidget(self.btn_copy_selected)

        # Copy All Button
        self.btn_copy_all = QPushButton("📄 Copy All", self)
        self.btn_copy_all.setToolTip("Copy complete transcript text to clipboard")
        self.btn_copy_all.clicked.connect(self._copy_all)
        tool_bar.addWidget(self.btn_copy_all)

        # Save Changes Button
        self.btn_save_changes = QPushButton("💾 Save Changes", self)
        self.btn_save_changes.setProperty("class", "primary-btn")
        self.btn_save_changes.setToolTip("Save manual transcript corrections to database")
        self.btn_save_changes.clicked.connect(self._save_manual_edits)
        tool_bar.addWidget(self.btn_save_changes)

        # Look Up Meaning Button
        self.btn_lookup = QPushButton("📖 Look Up", self)
        self.btn_lookup.setToolTip("Look up word meaning and save to Vocabulary")
        self.btn_lookup.clicked.connect(self._open_lookup_for_selected)
        tool_bar.addWidget(self.btn_lookup)

        # View Mode Switcher
        self.combo_view_mode = QComboBox(self)
        self.combo_view_mode.addItem("📝 Text Editor", 0)
        self.combo_view_mode.addItem("📑 Segment Cards", 1)
        self.combo_view_mode.currentIndexChanged.connect(self._on_view_mode_changed)
        tool_bar.addWidget(self.combo_view_mode)

        # Auto-scroll checkbox
        self.chk_autoscroll = QCheckBox("Auto-scroll", self)
        self.chk_autoscroll.setChecked(True)
        self.chk_autoscroll.toggled.connect(self._on_autoscroll_toggled)
        tool_bar.addWidget(self.chk_autoscroll)

        # Clear View Button
        self.btn_clear = QPushButton("Clear View", self)
        self.btn_clear.clicked.connect(self.clear_transcript_view)
        tool_bar.addWidget(self.btn_clear)

        layout.addLayout(tool_bar)

        # 3. Status / Notification Banner
        self.lbl_status_message = QLabel("", self)
        self.lbl_status_message.setStyleSheet(
            "background-color: #1A2234; border: 1px solid #2563EB; color: #93C5FD; "
            "font-size: 12px; font-weight: 500; padding: 6px 12px; border-radius: 6px;"
        )
        self.lbl_status_message.setVisible(False)
        layout.addWidget(self.lbl_status_message)

        # 4. Central Stack: Text Editor (Index 0) vs Segment Cards (Index 1)
        self.content_stack = QStackedWidget(self)

        # View 0: TranscriptEditorWidget (QPlainTextEdit based, selectable and editable)
        self.transcript_editor = TranscriptEditorWidget(self.content_stack)
        self.transcript_editor.lookup_requested.connect(self._open_lookup_dialog)
        self.transcript_editor.save_requested.connect(self._save_manual_edits)
        self.content_stack.addWidget(self.transcript_editor)

        # View 1: Scrollable Segment Cards
        self.scroll_area = QScrollArea(self.content_stack)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.segments_layout = QVBoxLayout(self.scroll_content)
        self.segments_layout.setContentsMargins(0, 0, 0, 0)
        self.segments_layout.setSpacing(10)
        self.segments_layout.addStretch()

        self.scroll_area.setWidget(self.scroll_content)
        self.content_stack.addWidget(self.scroll_area)

        layout.addWidget(self.content_stack, stretch=1)

        # Empty State Placeholder (for cards view)
        self.empty_label = QLabel(
            "Ready to transcribe.\nClick 'Start' above to begin capturing speech from your computer.",
            self.scroll_content,
        )
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color: #64748B; font-size: 14px; padding: 60px 0;")
        self.segments_layout.insertWidget(0, self.empty_label)

    def set_status_message(self, message: str, visible: bool = True) -> None:
        """Display an operational or confirmation status message."""
        self.lbl_status_message.setText(message)
        self.lbl_status_message.setVisible(visible and bool(message))

    def _handle_start(self) -> None:
        self._is_running = True
        self._is_paused = False
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_stop.setEnabled(True)
        self.combo_source.setEnabled(False)
        self.empty_label.setText(
            "🎧 Listening for speech...\nPlay any video, reel, or meeting audio on your computer."
        )
        self.empty_label.setVisible(len(self._segments) == 0)
        self._timer.start()
        self.start_clicked.emit()

    def _handle_pause(self) -> None:
        if not self._is_paused:
            self._is_paused = True
            self.btn_pause.setText("▶  Resume")
            self._timer.stop()
        else:
            self._is_paused = False
            self.btn_pause.setText("⏸  Pause")
            self._timer.start()
        self.pause_clicked.emit()

    def _handle_stop(self) -> None:
        self._is_running = False
        self._is_paused = False
        self._timer.stop()
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_pause.setText("⏸  Pause")
        self.btn_stop.setEnabled(False)
        self.combo_source.setEnabled(True)
        self.stop_clicked.emit()

    def _on_device_selection_changed(self, index: int) -> None:
        item = self.combo_source.itemData(index)
        if item:
            device_id, source_type = item
            self.source_changed.emit(source_type)
            self.device_changed.emit(device_id, source_type)

    def set_devices(self, loopback_devices: list, mic_devices: list) -> None:
        """Populate the device dropdown with real WASAPI playback loopbacks and microphones."""
        self.combo_source.blockSignals(True)
        self.combo_source.clear()

        for dev in loopback_devices:
            label = f"🔊 Loopback: {dev.name}"
            if dev.is_default:
                label += " (Default)"
            self.combo_source.addItem(label, (dev.id, AudioSourceType.SYSTEM_LOOPBACK))

        for dev in mic_devices:
            label = f"🎤 Mic: {dev.name}"
            if dev.is_default:
                label += " (Default)"
            self.combo_source.addItem(label, (dev.id, AudioSourceType.MICROPHONE))

        self.combo_source.blockSignals(False)

    def set_audio_level(self, linear_level: float, rms_db: float) -> None:
        """Forward audio levels to the control bar audio meter."""
        self.audio_meter.set_level(linear_level, rms_db)

    def _on_view_mode_changed(self, index: int) -> None:
        """Toggle between Text Editor and Card Stream."""
        mode_idx = self.combo_view_mode.currentData()
        self.content_stack.setCurrentIndex(mode_idx)
        if mode_idx == 0:
            # Sync any card updates to editor
            self.transcript_editor.set_segments(self._segments)

    def _on_autoscroll_toggled(self, checked: bool) -> None:
        self._auto_scroll = checked

    def _on_timer_tick(self) -> None:
        self._elapsed_seconds += 1
        hours, remainder = divmod(self._elapsed_seconds, 3600)
        mins, secs = divmod(remainder, 60)
        self.lbl_timer.setText(f"{hours:02d}:{mins:02d}:{secs:02d}")

    def add_segment(self, segment: TranscriptSegment) -> None:
        """Append a new transcript segment to both the editor and cards."""
        self.empty_label.setVisible(False)
        self._segments.append(segment)
        if not self.active_session_id:
            self.active_session_id = segment.session_id

        # 1. Update text editor
        self.transcript_editor.append_segment(segment)

        # 2. Update card view
        card = SegmentCard(segment, display_mode=self._display_mode, parent=self.scroll_content)
        card.lookup_requested.connect(self._open_lookup_dialog)
        card.edit_saved.connect(self._on_card_segment_edited)
        self._cards.append(card)

        insert_idx = max(0, self.segments_layout.count() - 1)
        self.segments_layout.insertWidget(insert_idx, card)

        if self._auto_scroll:
            if self.content_stack.currentIndex() == 0:
                self.transcript_editor.moveCursor(QTextCursor.MoveOperation.End)
            else:
                QTimer.singleShot(50, self._scroll_to_bottom)

    def _on_card_segment_edited(self, segment_id: str, new_text: str) -> None:
        """Handle inline edit from a segment card."""
        for seg in self._segments:
            if seg.id == segment_id:
                seg.original_text = new_text
                break
        self.transcript_editor.set_segments(self._segments)
        if self.segment_repo:
            self.segment_repo.update_segment_text(segment_id, new_text)
            self.set_status_message("✓ Segment text updated in database.", visible=True)

    def _copy_selected_or_all(self) -> None:
        """Copy selected text, or full transcript if nothing selected."""
        copied = self.transcript_editor.copy_selected()
        if not copied:
            # Check cards selection
            for card in self._cards:
                if card.lbl_orig.hasSelectedText():
                    QApplication.clipboard().setText(card.lbl_orig.selectedText())
                    copied = True
                    break
        if not copied:
            # Fallback to copying all text
            self.transcript_editor.copy_all()
            self.set_status_message("📄 Complete transcript copied to clipboard!", visible=True)
        else:
            self.set_status_message("📋 Selected text copied to clipboard!", visible=True)
        QTimer.singleShot(3000, lambda: self.set_status_message("", visible=False))

    def _copy_all(self) -> None:
        """Copy full transcript text."""
        self.transcript_editor.copy_all()
        self.set_status_message("📄 Complete transcript copied to clipboard!", visible=True)
        QTimer.singleShot(3000, lambda: self.set_status_message("", visible=False))

    def _save_manual_edits(self) -> None:
        """Parse manual corrections from editor and persist to SQLite."""
        session_id = self.active_session_id or ""
        parsed = self.transcript_editor.parse_edited_segments(session_id)
        if not parsed:
            self.set_status_message("⚠️ No transcript text to save.", visible=True)
            return

        self._segments = parsed
        if self.segment_repo and session_id:
            try:
                self.segment_repo.save_session_segments(session_id, self._segments)
                self.set_status_message("✓ Manual edits saved to database!", visible=True)
                self._rebuild_segment_cards()
            except Exception as exc:
                logger.error("Failed to save transcript edits: %s", exc)
                self.set_status_message(f"⚠️ Error saving edits: {exc}", visible=True)
        else:
            self.set_status_message("✓ Edits updated in editor (session not yet saved).", visible=True)
            self._rebuild_segment_cards()

        QTimer.singleShot(4000, lambda: self.set_status_message("", visible=False))

    def _open_lookup_for_selected(self) -> None:
        """Look up currently selected text from editor or cards."""
        text = self.transcript_editor.get_selected_text()
        context = self.transcript_editor.get_surrounding_sentence()

        if not text:
            # Check if text is selected in any card
            for card in self._cards:
                if card.lbl_orig.hasSelectedText():
                    text = card.lbl_orig.selectedText()
                    context = card.segment.original_text
                    break

        self._open_lookup_dialog(text, context)

    def _open_lookup_dialog(self, word: str, context: str) -> None:
        """Display WordLookupDialog to look up definition and save to vocabulary."""
        if not self.vocab_repo:
            QMessageBox.warning(self, "Vocabulary", "Vocabulary repository is not initialized.")
            return

        dialog = WordLookupDialog(
            vocab_repo=self.vocab_repo,
            initial_word=word,
            initial_context=context,
            source_session_id=self.active_session_id,
            parent=self,
        )
        dialog.vocabulary_saved.connect(self._on_vocabulary_saved)
        dialog.exec()

    def _on_vocabulary_saved(self, entry) -> None:
        """Handle newly saved vocabulary entry."""
        self.set_status_message(f"✓ Saved '{entry.word_or_phrase}' to Vocabulary!", visible=True)
        self.vocabulary_added.emit(entry)
        QTimer.singleShot(4000, lambda: self.set_status_message("", visible=False))

    def clear_transcript_view(self) -> None:
        """Clear visible cards and editor without altering the database."""
        self._segments.clear()
        self._cards.clear()
        self.transcript_editor.clear()
        while self.segments_layout.count() > 1:
            item = self.segments_layout.takeAt(0)
            if item.widget() and item.widget() != self.empty_label:
                item.widget().deleteLater()
        self.empty_label.setVisible(True)
        self.clear_clicked.emit()

    def _rebuild_segment_cards(self) -> None:
        """Re-render cards with the current segments."""
        for i in reversed(range(self.segments_layout.count() - 1)):
            item = self.segments_layout.itemAt(i)
            if item.widget() and item.widget() != self.empty_label:
                w = self.segments_layout.takeAt(i).widget()
                if w:
                    w.deleteLater()
        self._cards.clear()

        for seg in self._segments:
            card = SegmentCard(seg, display_mode=self._display_mode, parent=self.scroll_content)
            card.lookup_requested.connect(self._open_lookup_dialog)
            card.edit_saved.connect(self._on_card_segment_edited)
            self._cards.append(card)
            self.segments_layout.insertWidget(max(0, self.segments_layout.count() - 1), card)

    def _filter_segments(self, query: str) -> None:
        """Filter segments visible in view based on query string."""
        query = query.strip().lower()
        for card in self._cards:
            orig = card.segment.original_text.lower()
            trans = (card.segment.translated_text or "").lower()
            match = (query in orig) or (query in trans)
            card.setVisible(match)

    def _scroll_to_bottom(self) -> None:
        v_bar = self.scroll_area.verticalScrollBar()
        if v_bar:
            v_bar.setValue(v_bar.maximum())
