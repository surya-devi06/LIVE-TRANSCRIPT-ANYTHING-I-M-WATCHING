"""Application logging setup with rotating file handler and secret sanitization."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import re
from typing import Optional

_INITIALIZED = False

# Pattern to redact potential API keys or tokens from logs
SECRET_PATTERN = re.compile(
    r"(sk-[a-zA-Z0-9_\-]{20,}|key=[a-zA-Z0-9_\-]{16,}|bearer\s+[a-zA-Z0-9_\-\.]{20,})",
    re.IGNORECASE,
)


class SecretFilter(logging.Filter):
    """Filter that masks potential secrets in log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = SECRET_PATTERN.sub("[REDACTED_SECRET]", record.msg)
        return True


class SafeStreamHandler(logging.StreamHandler):
    """Stream handler that safely tolerates dynamically closed test streams."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            if self.stream and not getattr(self.stream, "closed", False):
                super().emit(record)
        except (ValueError, OSError):
            pass


def setup_logging(
    log_dir: Path,
    log_level: str = "INFO",
    max_bytes: int = 5 * 1024 * 1024,  # 5 MB
    backup_count: int = 3,
) -> None:
    """Initialize root logging with both rotating file and console handlers."""
    global _INITIALIZED
    if _INITIALIZED:
        return

    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "live_transcript.log"

    level = getattr(logging, log_level.upper(), logging.INFO)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)-7s] %(name)s (%(threadName)s): %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    secret_filter = SecretFilter()

    # 1. Rotating File Handler (UTF-8)
    file_handler = RotatingFileHandler(
        filename=str(log_file),
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(secret_filter)
    root_logger.addHandler(file_handler)

    # 2. Console Handler with SafeStreamHandler
    console_handler = SafeStreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(secret_filter)
    root_logger.addHandler(console_handler)

    _INITIALIZED = True
    logging.getLogger("live_transcript.logging").info(
        "Logging initialized. Log file: %s (Level: %s)", log_file, log_level
    )


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Retrieve a namespaced application logger."""
    if name:
        return logging.getLogger(f"live_transcript.{name}")
    return logging.getLogger("live_transcript")
