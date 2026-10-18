"""Platform utilities and path helpers."""

import os
import platform
import re
from pathlib import Path


def is_windows() -> bool:
    """Return True if the running OS is Windows."""
    return platform.system().lower() == "windows"


def get_default_data_dir() -> Path:
    """Return the base directory for persistent application storage.

    On Windows, uses %LOCALAPPDATA%/LiveTranscript.
    Falls back to ~/.live_transcript on other platforms or if variable is unset.
    """
    if is_windows():
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            base = Path(local_app_data) / "LiveTranscript"
            base.mkdir(parents=True, exist_ok=True)
            return base

    base = Path.home() / ".live_transcript"
    base.mkdir(parents=True, exist_ok=True)
    return base


def get_resource_path(relative_path: str = "") -> Path:
    """Return the absolute path to a bundled resource.

    Works for normal Python execution as well as PyInstaller frozen bundles
    (which extract or mount resources to sys._MEIPASS).
    """
    import sys

    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        # 4 levels up: utils -> live_transcript -> src -> project root
        base_path = Path(__file__).resolve().parent.parent.parent.parent

    return (base_path / relative_path) if relative_path else base_path


def sanitize_filename(filename: str, replacement: str = "_") -> str:
    """Sanitize a string to be a safe filename across operating systems.

    Strips Windows-reserved characters: < > : " / \\ | ? *
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', replacement, filename)
    # Remove trailing dots and spaces (Windows restriction)
    sanitized = sanitized.strip(". ")
    # Fallback if empty
    return sanitized if sanitized else "transcript"

