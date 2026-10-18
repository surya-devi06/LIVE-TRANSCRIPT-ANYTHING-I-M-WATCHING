"""Vocabulary view to browse and manage saved words, phrases, and explanations."""

from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from live_transcript.database.models import VocabularyEntry
from live_transcript.database.repositories import VocabularyRepository
from live_transcript.ui.dialogs.word_lookup_dialog import WordLookupDialog


class VocabularyView(QWidget):
    """View to review, search, and manage saved vocabulary terms."""

    def __init__(
        self,
        vocab_repo: VocabularyRepository,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.vocab_repo = vocab_repo
        self._entries: list[VocabularyEntry] = []

        self._setup_ui()
        self.refresh()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Header Title
        title = QLabel("Vocabulary & Learning", self)
        title.setProperty("class", "view-title")
        desc = QLabel("Review words, phrases, and definitions saved during your sessions.", self)
        desc.setProperty("class", "view-desc")
        layout.addWidget(title)
        layout.addWidget(desc)

        # Search & Action Bar
        search_bar = QHBoxLayout()
        search_bar.setSpacing(10)

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("🔍  Search saved vocabulary by word or meaning...")
        self.search_input.textChanged.connect(self._on_search_changed)
        search_bar.addWidget(self.search_input, stretch=1)

        self.btn_add = QPushButton("➕  Add Word", self)
        self.btn_add.setToolTip("Look up or manually add a new word to your vocabulary")
        self.btn_add.clicked.connect(self._on_add_clicked)
        search_bar.addWidget(self.btn_add)

        self.btn_edit = QPushButton("✏️  Edit", self)
        self.btn_edit.setEnabled(False)
        self.btn_edit.setToolTip("Edit the selected vocabulary entry")
        self.btn_edit.clicked.connect(self._on_edit_clicked)
        search_bar.addWidget(self.btn_edit)

        self.btn_delete = QPushButton("🗑  Delete", self)
        self.btn_delete.setProperty("class", "danger-btn")
        self.btn_delete.setEnabled(False)
        self.btn_delete.setToolTip("Delete the selected vocabulary item")
        self.btn_delete.clicked.connect(self._on_delete_clicked)
        search_bar.addWidget(self.btn_delete)

        self.btn_refresh = QPushButton("🔄  Refresh", self)
        self.btn_refresh.clicked.connect(self.refresh)
        search_bar.addWidget(self.btn_refresh)

        layout.addLayout(search_bar)

        # Table
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Word / Phrase",
            "Meaning",
            "Original Context",
            "Date Saved",
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.cellDoubleClicked.connect(lambda r, c: self._on_edit_clicked())

        layout.addWidget(self.table)

        # Empty State
        self.empty_lbl = QLabel(
            "<b>No vocabulary items saved yet.</b><br><br>"
            "• Click <b>➕ Add Word</b> above to look up and save any word or phrase.<br>"
            "• Or while viewing a live transcript or history session, select any text and click "
            "<b>🔍 Look Up Meaning</b> to save it along with its context sentence.",
            self,
        )
        self.empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_lbl.setStyleSheet(
            "color: #94A3B8; font-size: 14px; padding: 48px; line-height: 1.6;"
        )
        self.empty_lbl.setVisible(False)
        layout.addWidget(self.empty_lbl)

    def refresh(self) -> None:
        """Reload saved entries from SQLite."""
        query = self.search_input.text().strip()
        if query:
            self._entries = self.vocab_repo.search(query)
        else:
            self._entries = self.vocab_repo.list_all(limit=100)

        self._populate_table()

    def _populate_table(self) -> None:
        self.table.setRowCount(0)
        has_items = len(self._entries) > 0
        self.table.setVisible(has_items)
        self.empty_lbl.setVisible(not has_items)
        self.btn_edit.setEnabled(False)
        self.btn_delete.setEnabled(False)

        for row_idx, entry in enumerate(self._entries):
            self.table.insertRow(row_idx)

            # Word / Phrase
            item_word = QTableWidgetItem(entry.word_or_phrase)
            item_word.setData(Qt.ItemDataRole.UserRole, entry.id)
            self.table.setItem(row_idx, 0, item_word)

            # Meaning
            self.table.setItem(row_idx, 1, QTableWidgetItem(entry.meaning))

            # Original Context
            self.table.setItem(row_idx, 2, QTableWidgetItem(entry.original_sentence or "-"))

            # Date
            created = entry.created_at[:10] if entry.created_at else "-"
            self.table.setItem(row_idx, 3, QTableWidgetItem(created))

    def _on_search_changed(self, text: str) -> None:
        self.refresh()

    def _on_selection_changed(self) -> None:
        has_sel = len(self.table.selectionModel().selectedRows()) > 0
        self.btn_edit.setEnabled(has_sel)
        self.btn_delete.setEnabled(has_sel)

    def _get_selected_entry(self) -> Optional[VocabularyEntry]:
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        row = selected_rows[0].row()
        entry_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        for entry in self._entries:
            if entry.id == entry_id:
                return entry
        return None

    def _on_add_clicked(self) -> None:
        dialog = WordLookupDialog(vocab_repo=self.vocab_repo, parent=self)
        if dialog.exec():
            self.refresh()

    def _on_edit_clicked(self) -> None:
        entry = self._get_selected_entry()
        if not entry:
            return

        dialog = WordLookupDialog(
            vocab_repo=self.vocab_repo,
            initial_word=entry.word_or_phrase,
            initial_context=entry.original_sentence,
            existing_entry=entry,
            parent=self,
        )
        if dialog.exec():
            self.refresh()

    def _on_delete_clicked(self) -> None:
        entry = self._get_selected_entry()
        if not entry:
            return

        confirm = QMessageBox.question(
            self,
            "Delete Vocabulary",
            f"Are you sure you want to delete '{entry.word_or_phrase}' from your saved vocabulary?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.vocab_repo.delete(entry.id)
            self.refresh()
