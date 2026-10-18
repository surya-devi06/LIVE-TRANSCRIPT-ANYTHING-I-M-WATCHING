"""Dialog for dictionary lookup and vocabulary saving/editing."""

from typing import Optional
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from live_transcript.database.models import VocabularyEntry
from live_transcript.database.repositories import VocabularyRepository
from live_transcript.services.dictionary_service import DictionaryResult, DictionaryService
from live_transcript.utils.logging_setup import get_logger

logger = get_logger("ui.dialogs.word_lookup")


class _LookupWorker(QThread):
    """Background worker thread for fetching dictionary definitions."""
    result_ready = Signal(object)  # (DictionaryResult)

    def __init__(self, service: DictionaryService, word: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.service = service
        self.word = word

    def run(self) -> None:
        res = self.service.lookup(self.word)
        self.result_ready.emit(res)


class WordLookupDialog(QDialog):
    """Dialog allowing users to look up words, view definitions, and save/edit vocabulary."""

    vocabulary_saved = Signal(object)  # (VocabularyEntry)

    def __init__(
        self,
        vocab_repo: VocabularyRepository,
        initial_word: str = "",
        initial_context: str = "",
        source_session_id: Optional[str] = None,
        existing_entry: Optional[VocabularyEntry] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.vocab_repo = vocab_repo
        self.source_session_id = source_session_id
        self.existing_entry = existing_entry
        self.dictionary_service = DictionaryService()
        self._lookup_thread: Optional[_LookupWorker] = None

        self.setWindowTitle("Save to Vocabulary" if not existing_entry else "Edit Vocabulary Entry")
        self.setMinimumWidth(500)
        self.resize(520, 480)

        self._setup_ui(initial_word, initial_context)

        if self.existing_entry:
            self._load_existing_entry(self.existing_entry)
        elif initial_word.strip():
            self._trigger_lookup()

    def _setup_ui(self, initial_word: str, initial_context: str) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Dialog Title & Description
        title_lbl = QLabel("📖 Vocabulary Learning", self)
        title_lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #38BDF8;")
        desc_lbl = QLabel(
            "Look up definitions and save unfamiliar words or phrases to review later.",
            self,
        )
        desc_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")
        layout.addWidget(title_lbl)
        layout.addWidget(desc_lbl)

        form = QFormLayout()
        form.setSpacing(10)

        # Word / Phrase input + Lookup Button
        word_box = QHBoxLayout()
        self.input_word = QLineEdit(initial_word.strip(), self)
        self.input_word.setPlaceholderText("Enter word or phrase...")
        self.input_word.returnPressed.connect(self._trigger_lookup)

        self.btn_lookup = QPushButton("🔍 Look Up", self)
        self.btn_lookup.clicked.connect(self._trigger_lookup)

        word_box.addWidget(self.input_word, stretch=1)
        word_box.addWidget(self.btn_lookup)
        form.addRow("Word / Phrase:", word_box)

        # Status label (Lookup status)
        self.lbl_status = QLabel("", self)
        self.lbl_status.setStyleSheet("font-size: 11px; color: #94A3B8;")
        form.addRow("", self.lbl_status)

        # Meaning / Definition
        self.input_meaning = QPlainTextEdit(self)
        self.input_meaning.setPlaceholderText("Definition or meaning...")
        self.input_meaning.setMaximumHeight(110)
        form.addRow("Meaning:", self.input_meaning)

        # Original Context
        self.input_context = QPlainTextEdit(initial_context.strip(), self)
        self.input_context.setPlaceholderText("Sentence from transcript where this word appeared...")
        self.input_context.setMaximumHeight(80)
        form.addRow("Context:", self.input_context)

        # Example Sentence (optional)
        self.input_example = QLineEdit(self)
        self.input_example.setPlaceholderText("Optional example sentence...")
        form.addRow("Example:", self.input_example)

        layout.addLayout(form)

        # Action Buttons
        btn_box = QHBoxLayout()
        btn_box.addStretch()

        self.btn_cancel = QPushButton("Cancel", self)
        self.btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(self.btn_cancel)

        save_label = "💾 Save to Vocabulary" if not self.existing_entry else "💾 Update Entry"
        self.btn_save = QPushButton(save_label, self)
        self.btn_save.setProperty("class", "primary-btn")
        self.btn_save.clicked.connect(self._save_entry)
        btn_box.addWidget(self.btn_save)

        layout.addLayout(btn_box)

    def _load_existing_entry(self, entry: VocabularyEntry) -> None:
        """Prepopulate fields when editing an existing entry."""
        self.input_word.setText(entry.word_or_phrase)
        self.input_meaning.setPlainText(entry.meaning)
        self.input_context.setPlainText(entry.original_sentence)
        self.input_example.setText(entry.example_sentence)

    def _trigger_lookup(self) -> None:
        """Start background lookup thread for the current word."""
        word = self.input_word.text().strip()
        if not word:
            self.lbl_status.setText("⚠️ Please enter a word to look up.")
            self.lbl_status.setStyleSheet("color: #F87171; font-size: 11px;")
            return

        self.lbl_status.setText("Searching dictionary...")
        self.lbl_status.setStyleSheet("color: #38BDF8; font-size: 11px;")
        self.btn_lookup.setEnabled(False)

        self._lookup_thread = _LookupWorker(self.dictionary_service, word, parent=self)
        self._lookup_thread.result_ready.connect(self._on_lookup_complete)
        self._lookup_thread.start()

    def _on_lookup_complete(self, res: DictionaryResult) -> None:
        """Handle dictionary lookup result on main thread."""
        self.btn_lookup.setEnabled(True)
        if res.found:
            self.input_meaning.setPlainText(res.meaning)
            if res.example and not self.input_example.text():
                self.input_example.setText(res.example)
            phonetic_str = f" [{res.phonetic}]" if res.phonetic else ""
            self.lbl_status.setText(f"✓ Definition found{phonetic_str}")
            self.lbl_status.setStyleSheet("color: #34D399; font-size: 11px;")
        else:
            msg = res.error_message or "Definition not found online. You can type the meaning manually."
            self.lbl_status.setText(msg)
            self.lbl_status.setStyleSheet("color: #FBBF24; font-size: 11px;")

    def _save_entry(self) -> None:
        """Validate and persist vocabulary entry in SQLite."""
        word = self.input_word.text().strip()
        meaning = self.input_meaning.toPlainText().strip()
        context = self.input_context.toPlainText().strip()
        example = self.input_example.text().strip()

        if not word:
            self.lbl_status.setText("⚠️ Word or phrase cannot be empty.")
            self.lbl_status.setStyleSheet("color: #F87171; font-size: 11px;")
            return

        if not meaning:
            self.lbl_status.setText("⚠️ Please provide a definition or meaning.")
            self.lbl_status.setStyleSheet("color: #F87171; font-size: 11px;")
            return

        try:
            if self.existing_entry:
                # Update existing entry
                self.existing_entry.word_or_phrase = word
                self.existing_entry.meaning = meaning
                self.existing_entry.original_sentence = context
                self.existing_entry.example_sentence = example
                self.vocab_repo.update(self.existing_entry)
                entry = self.existing_entry
                logger.info("Updated vocabulary entry: '%s'", word)
            else:
                # Create new entry
                entry = VocabularyEntry.create_new(
                    word_or_phrase=word,
                    original_sentence=context,
                    meaning=meaning,
                    example_sentence=example,
                    source_session_id=self.source_session_id,
                )
                self.vocab_repo.add(entry)
                logger.info("Created new vocabulary entry: '%s'", word)

            self.vocabulary_saved.emit(entry)
            self.accept()
        except Exception as exc:
            logger.error("Failed to save vocabulary entry: %s", exc)
            self.lbl_status.setText(f"Error saving: {exc}")
            self.lbl_status.setStyleSheet("color: #F87171; font-size: 11px;")
