"""History view to browse, search, open, edit, and manage historical transcription sessions."""

from typing import List, Optional
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from live_transcript.database.models import Session, TranscriptSegment
from live_transcript.database.repositories import SegmentRepository, SessionRepository, VocabularyRepository
from live_transcript.ui.dialogs.word_lookup_dialog import WordLookupDialog
from live_transcript.ui.widgets.transcript_editor import TranscriptEditorWidget
from live_transcript.utils.logging_setup import get_logger

logger = get_logger("ui.views.history")


class HistoryView(QWidget):
    """View to review, search, open, edit, and manage historical transcription sessions."""

    session_selected = Signal(str)
    vocabulary_added = Signal(object)  # (VocabularyEntry)

    def __init__(
        self,
        session_repo: SessionRepository,
        segment_repo: SegmentRepository,
        vocab_repo: Optional[VocabularyRepository] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.session_repo = session_repo
        self.segment_repo = segment_repo
        self.vocab_repo = vocab_repo

        self._sessions: List[Session] = []
        self._current_session: Optional[Session] = None
        self._current_segments: List[TranscriptSegment] = []

        self._setup_ui()
        self.refresh()

    def set_vocab_repository(self, vocab_repo: VocabularyRepository) -> None:
        """Assign vocabulary repository for word lookup."""
        self.vocab_repo = vocab_repo

    def _setup_ui(self) -> None:
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget(self)
        root_layout.addWidget(self.stack)

        # Page 0: Sessions Table List View
        self.page_list = QWidget(self.stack)
        self._setup_list_page(self.page_list)
        self.stack.addWidget(self.page_list)  # Index 0

        # Page 1: Session Detail & Editor View
        self.page_detail = QWidget(self.stack)
        self._setup_detail_page(self.page_detail)
        self.stack.addWidget(self.page_detail)  # Index 1

        self.stack.setCurrentIndex(0)

    # -------------------------------------------------------------------------
    # Page 0: Sessions List
    # -------------------------------------------------------------------------
    def _setup_list_page(self, page: QWidget) -> None:
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Header Title
        title = QLabel("Session History", page)
        title.setProperty("class", "view-title")
        desc = QLabel("Review, open, search, and manage previously transcribed sessions.", page)
        desc.setProperty("class", "view-desc")
        layout.addWidget(title)
        layout.addWidget(desc)

        # Search Bar & Actions
        search_bar = QHBoxLayout()
        search_bar.setSpacing(10)

        self.search_input = QLineEdit(page)
        self.search_input.setPlaceholderText("🔍  Search sessions by title or transcript words...")
        self.search_input.textChanged.connect(self._on_search_changed)
        search_bar.addWidget(self.search_input, stretch=1)

        # Sort Dropdown
        self.combo_sort = QComboBox(page)
        self.combo_sort.addItem("📅 Newest First", "date_desc")
        self.combo_sort.addItem("📅 Oldest First", "date_asc")
        self.combo_sort.addItem("🔤 Title (A-Z)", "title_asc")
        self.combo_sort.addItem("⏱ Duration", "duration_desc")
        self.combo_sort.currentIndexChanged.connect(self.refresh)
        search_bar.addWidget(self.combo_sort)

        self.btn_open = QPushButton("📂 Open Session", page)
        self.btn_open.setProperty("class", "primary-btn")
        self.btn_open.setEnabled(False)
        self.btn_open.clicked.connect(self._on_open_clicked)
        search_bar.addWidget(self.btn_open)

        self.btn_delete = QPushButton("🗑  Delete", page)
        self.btn_delete.setProperty("class", "danger-btn")
        self.btn_delete.setEnabled(False)
        self.btn_delete.clicked.connect(self._on_delete_clicked)
        search_bar.addWidget(self.btn_delete)

        self.btn_refresh = QPushButton("🔄  Refresh", page)
        self.btn_refresh.clicked.connect(self.refresh)
        search_bar.addWidget(self.btn_refresh)

        layout.addLayout(search_bar)

        # Sessions Table
        self.table = QTableWidget(page)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Title",
            "Started At",
            "Duration",
            "Segments",
            "Language",
            "Transcript Preview",
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.doubleClicked.connect(self._on_row_double_clicked)

        layout.addWidget(self.table)

        # Empty State Label
        self.empty_lbl = QLabel(
            "No saved sessions found.\nStart a live transcription from the Live Transcript page to record your first session.",
            page,
        )
        self.empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_lbl.setStyleSheet("color: #64748B; font-size: 14px; padding: 60px 0; line-height: 1.5;")
        self.empty_lbl.setVisible(False)
        layout.addWidget(self.empty_lbl)

    # -------------------------------------------------------------------------
    # Page 1: Session Detail & Editor
    # -------------------------------------------------------------------------
    def _setup_detail_page(self, page: QWidget) -> None:
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Top Navigation Bar
        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        self.btn_back = QPushButton("⬅ Back to Sessions", page)
        self.btn_back.clicked.connect(self.close_detail_view)
        top_bar.addWidget(self.btn_back)

        top_bar.addStretch()

        # Session metadata tag
        self.lbl_detail_meta = QLabel("", page)
        self.lbl_detail_meta.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 500;")
        top_bar.addWidget(self.lbl_detail_meta)

        self.btn_delete_detail = QPushButton("🗑 Delete Session", page)
        self.btn_delete_detail.setProperty("class", "danger-btn")
        self.btn_delete_detail.clicked.connect(self._on_delete_detail_clicked)
        top_bar.addWidget(self.btn_delete_detail)

        layout.addLayout(top_bar)

        # Session Header Card (Title & Rename)
        title_card = QFrame(page)
        title_card.setProperty("class", "card")
        tc_layout = QHBoxLayout(title_card)
        tc_layout.setContentsMargins(12, 10, 12, 10)
        tc_layout.setSpacing(10)

        lbl_t = QLabel("Title:", title_card)
        lbl_t.setStyleSheet("font-weight: 600; color: #94A3B8;")
        self.input_session_title = QLineEdit(title_card)
        self.input_session_title.setStyleSheet("font-size: 15px; font-weight: 600; color: #F8FAFC;")
        self.btn_save_title = QPushButton("Save Title", title_card)
        self.btn_save_title.clicked.connect(self._save_session_title)

        tc_layout.addWidget(lbl_t)
        tc_layout.addWidget(self.input_session_title, stretch=1)
        tc_layout.addWidget(self.btn_save_title)
        layout.addWidget(title_card)

        # Transcript Actions Toolbar
        actions_bar = QHBoxLayout()
        actions_bar.setSpacing(10)

        self.btn_copy_selected = QPushButton("📋 Copy Selected", page)
        self.btn_copy_selected.clicked.connect(self._copy_selected)
        actions_bar.addWidget(self.btn_copy_selected)

        self.btn_copy_all = QPushButton("📄 Copy All", page)
        self.btn_copy_all.clicked.connect(self._copy_all)
        actions_bar.addWidget(self.btn_copy_all)

        self.btn_save_changes = QPushButton("💾 Save Changes", page)
        self.btn_save_changes.setProperty("class", "primary-btn")
        self.btn_save_changes.setToolTip("Save manual transcript corrections to database")
        self.btn_save_changes.clicked.connect(self._save_changes)
        actions_bar.addWidget(self.btn_save_changes)

        self.btn_lookup = QPushButton("📖 Look Up Meaning", page)
        self.btn_lookup.setToolTip("Look up word meaning and save to Vocabulary")
        self.btn_lookup.clicked.connect(self._open_lookup_for_selected)
        actions_bar.addWidget(self.btn_lookup)

        actions_bar.addStretch()
        layout.addLayout(actions_bar)

        # Feedback Banner
        self.lbl_detail_feedback = QLabel("", page)
        self.lbl_detail_feedback.setStyleSheet(
            "background-color: #1A2234; border: 1px solid #10B981; color: #6EE7B7; "
            "font-size: 12px; font-weight: 500; padding: 6px 12px; border-radius: 6px;"
        )
        self.lbl_detail_feedback.setVisible(False)
        layout.addWidget(self.lbl_detail_feedback)

        # Transcript Editor Widget
        self.transcript_editor = TranscriptEditorWidget(page)
        self.transcript_editor.lookup_requested.connect(self._open_lookup_dialog)
        self.transcript_editor.save_requested.connect(self._save_changes)
        layout.addWidget(self.transcript_editor, stretch=1)

    def set_feedback_message(self, message: str, visible: bool = True) -> None:
        """Display an operational message in detail view."""
        self.lbl_detail_feedback.setText(message)
        self.lbl_detail_feedback.setVisible(visible and bool(message))

    # -------------------------------------------------------------------------
    # Public Controller Methods
    # -------------------------------------------------------------------------
    def open_session(self, session_id: str) -> None:
        """Load and display the specified session into the detail editor view."""
        if not session_id:
            logger.warning("open_session called with empty session_id.")
            return

        session = self.session_repo.get_by_id(session_id)
        if not session:
            logger.warning("Session ID '%s' not found in database.", session_id)
            QMessageBox.warning(self, "Session Not Found", f"Session with ID '{session_id}' could not be found.")
            return

        self._current_session = session
        self.input_session_title.setText(session.title)

        # Load segments
        segments = self.segment_repo.get_by_session(session_id)
        self._current_segments = segments

        # Update metadata label
        started = session.started_at.replace("T", " ")[:19] if session.started_at else "-"
        mins = int(session.duration_seconds // 60)
        secs = int(session.duration_seconds % 60)
        meta_text = f"📅 {started}   ⏱ {mins}m {secs}s   🗣 {session.source_language}   🧩 {len(segments)} segments"
        self.lbl_detail_meta.setText(meta_text)

        # Populate transcript editor
        self.transcript_editor.set_segments(segments)
        self.set_feedback_message("", visible=False)

        # Switch to detail page
        self.stack.setCurrentIndex(1)
        logger.info("Opened session '%s' with %d segments in HistoryView.", session.title, len(segments))

    def close_detail_view(self) -> None:
        """Return to sessions table list view."""
        self.stack.setCurrentIndex(0)
        self.refresh()

    def refresh(self) -> None:
        """Reload sessions from the database applying search and sorting."""
        query = self.search_input.text().strip()
        sort_mode = self.combo_sort.currentData() if hasattr(self, "combo_sort") else "date_desc"

        try:
            if query:
                # Search by title
                sessions = self.session_repo.search(query)
            else:
                sessions = self.session_repo.list_recent(limit=150)

            # Apply sorting
            if sort_mode == "date_asc":
                sessions.sort(key=lambda s: s.created_at or "")
            elif sort_mode == "date_desc":
                sessions.sort(key=lambda s: s.created_at or "", reverse=True)
            elif sort_mode == "title_asc":
                sessions.sort(key=lambda s: (s.title or "").lower())
            elif sort_mode == "duration_desc":
                sessions.sort(key=lambda s: s.duration_seconds or 0.0, reverse=True)

            self._sessions = sessions
            self._populate_table()
        except Exception as exc:
            logger.error("Failed to load sessions in HistoryView: %s", exc)

    def _populate_table(self) -> None:
        self.table.setRowCount(0)
        has_items = len(self._sessions) > 0
        self.table.setVisible(has_items)
        self.empty_lbl.setVisible(not has_items)
        self.btn_open.setEnabled(False)
        self.btn_delete.setEnabled(False)

        for row_idx, s in enumerate(self._sessions):
            self.table.insertRow(row_idx)

            # 0. Title
            item_title = QTableWidgetItem(s.title or "Untitled Session")
            item_title.setData(Qt.ItemDataRole.UserRole, s.id)
            self.table.setItem(row_idx, 0, item_title)

            # 1. Started At
            started = s.started_at.replace("T", " ")[:19] if s.started_at else "-"
            self.table.setItem(row_idx, 1, QTableWidgetItem(started))

            # 2. Duration
            mins = int(s.duration_seconds // 60)
            secs = int(s.duration_seconds % 60)
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"{mins}m {secs:02d}s"))

            # 3. Segments count
            seg_count = self.segment_repo.count_for_session(s.id)
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(seg_count)))

            # 4. Language
            lang = f"{s.source_language} → {s.target_language}"
            self.table.setItem(row_idx, 4, QTableWidgetItem(lang))

            # 5. Transcript Preview snippet
            preview_text = ""
            if seg_count > 0:
                first_segs = self.segment_repo.get_by_session(s.id)
                if first_segs:
                    preview_text = " ".join([seg.original_text for seg in first_segs[:2]])
                    if len(preview_text) > 75:
                        preview_text = preview_text[:72] + "..."
            self.table.setItem(row_idx, 5, QTableWidgetItem(preview_text or "(No speech recorded)"))

    def _on_search_changed(self, text: str) -> None:
        self.refresh()

    def _on_selection_changed(self) -> None:
        selected_rows = self.table.selectionModel().selectedRows()
        has_selection = len(selected_rows) > 0
        self.btn_open.setEnabled(has_selection)
        self.btn_delete.setEnabled(has_selection)

    def _on_row_double_clicked(self) -> None:
        self._on_open_clicked()

    def _on_open_clicked(self) -> None:
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
        row = selected_rows[0].row()
        item = self.table.item(row, 0)
        if item:
            session_id = item.data(Qt.ItemDataRole.UserRole)
            self.open_session(session_id)
            self.session_selected.emit(session_id)

    def _on_delete_clicked(self) -> None:
        """Delete session selected in list view."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        session_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        session_title = self.table.item(row, 0).text()

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to permanently delete session '{session_title}'?\nAll transcript segments will be erased.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.session_repo.delete(session_id)
            self.refresh()

    def _on_delete_detail_clicked(self) -> None:
        """Delete currently opened session from detail view."""
        if not self._current_session:
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to permanently delete session '{self._current_session.title}'?\nAll transcript segments will be erased.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.session_repo.delete(self._current_session.id)
            self.close_detail_view()

    def _save_session_title(self) -> None:
        """Save updated title for the active session."""
        if not self._current_session:
            return
        new_title = self.input_session_title.text().strip()
        if new_title:
            self._current_session.title = new_title
            self.session_repo.update(self._current_session)
            self.set_feedback_message("✓ Session title updated!", visible=True)
            QTimer.singleShot(3000, lambda: self.set_feedback_message("", visible=False))

    def _copy_selected(self) -> None:
        """Copy selected text from transcript editor."""
        copied = self.transcript_editor.copy_selected()
        if copied:
            self.set_feedback_message("📋 Selected text copied to clipboard!", visible=True)
        else:
            self.transcript_editor.copy_all()
            self.set_feedback_message("📄 Complete transcript copied to clipboard!", visible=True)
        QTimer.singleShot(3000, lambda: self.set_feedback_message("", visible=False))

    def _copy_all(self) -> None:
        """Copy complete transcript text to clipboard."""
        self.transcript_editor.copy_all()
        self.set_feedback_message("📄 Complete transcript copied to clipboard!", visible=True)
        QTimer.singleShot(3000, lambda: self.set_feedback_message("", visible=False))

    def _save_changes(self) -> None:
        """Persist manual corrections in detail transcript editor to SQLite."""
        if not self._current_session:
            return

        parsed = self.transcript_editor.parse_edited_segments(self._current_session.id)
        if not parsed:
            self.set_feedback_message("⚠️ No text to save.", visible=True)
            return

        try:
            self.segment_repo.save_session_segments(self._current_session.id, parsed)
            self._current_segments = parsed
            self.set_feedback_message("✓ Transcript changes saved to database!", visible=True)
            QTimer.singleShot(3000, lambda: self.set_feedback_message("", visible=False))
            logger.info("Saved %d updated segments for session '%s'", len(parsed), self._current_session.id)
        except Exception as exc:
            logger.error("Failed to save transcript changes: %s", exc)
            self.set_feedback_message(f"⚠️ Error saving changes: {exc}", visible=True)

    def _open_lookup_for_selected(self) -> None:
        """Look up selected word from transcript editor in dictionary."""
        word = self.transcript_editor.get_selected_text()
        context = self.transcript_editor.get_surrounding_sentence()
        self._open_lookup_dialog(word, context)

    def _open_lookup_dialog(self, word: str, context: str) -> None:
        """Show dictionary lookup dialog."""
        if not self.vocab_repo:
            QMessageBox.warning(self, "Vocabulary", "Vocabulary repository is not available.")
            return

        session_id = self._current_session.id if self._current_session else None
        dialog = WordLookupDialog(
            vocab_repo=self.vocab_repo,
            initial_word=word,
            initial_context=context,
            source_session_id=session_id,
            parent=self,
        )
        dialog.vocabulary_saved.connect(self._on_vocabulary_saved)
        dialog.exec()

    def _on_vocabulary_saved(self, entry) -> None:
        self.set_feedback_message(f"✓ Saved '{entry.word_or_phrase}' to Vocabulary!", visible=True)
        self.vocabulary_added.emit(entry)
        QTimer.singleShot(4000, lambda: self.set_feedback_message("", visible=False))
