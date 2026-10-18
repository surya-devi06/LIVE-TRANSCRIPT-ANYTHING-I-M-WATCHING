"""Unit tests for logging and secret sanitization."""

import logging
from pathlib import Path
from live_transcript.utils.logging_setup import SecretFilter, setup_logging


def test_secret_filter_redacts_tokens() -> None:
    """Verify SecretFilter masks OpenAI/Anthropic/Bearer API keys."""
    filter_ = SecretFilter()

    # Test OpenAI-style secret
    record1 = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Using key sk-1234567890abcdef1234567890abcdef for request",
        args=(),
        exc_info=None,
    )
    filter_.filter(record1)
    assert "sk-" not in record1.msg
    assert "[REDACTED_SECRET]" in record1.msg

    # Test Bearer token
    record2 = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Authorization: Bearer mysecrettoken1234567890abcdef",
        args=(),
        exc_info=None,
    )
    filter_.filter(record2)
    assert "[REDACTED_SECRET]" in record2.msg


def test_setup_logging_creates_file(temp_data_dir: Path) -> None:
    """Verify setup_logging configures root logger and writes to log file."""
    log_dir = temp_data_dir / "logs"
    setup_logging(log_dir=log_dir, log_level="DEBUG")

    logger = logging.getLogger("live_transcript.test")
    logger.info("Test log entry message")

    log_file = log_dir / "live_transcript.log"
    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "Test log entry message" in content
