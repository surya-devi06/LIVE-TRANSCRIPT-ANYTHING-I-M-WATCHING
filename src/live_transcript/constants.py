"""Application-wide constants and enums."""

from enum import Enum

APP_NAME = "Live Transcript"
APP_VERSION = "0.1.0"
ORGANIZATION_NAME = "LiveTranscript"
DEFAULT_WINDOW_TITLE = f"{APP_NAME} v{APP_VERSION}"


class AppState(str, Enum):
    """Overall application runtime state."""
    READY = "Ready"
    INITIALIZING = "Initializing"
    CAPTURING = "Capturing Audio"
    TRANSCRIBING = "Transcribing"
    PAUSED = "Paused"
    STOPPED = "Stopped"
    ERROR = "Error"


class AudioSourceType(str, Enum):
    """Audio capture source types."""
    SYSTEM_LOOPBACK = "System Audio"
    MICROPHONE = "Microphone"


class SegmentStatus(str, Enum):
    """Transcript segment completion status."""
    PARTIAL = "partial"
    FINAL = "final"


class ExportFormat(str, Enum):
    """Supported transcript export formats."""
    TXT = "txt"
    SRT = "srt"
    VTT = "vtt"
    JSON = "json"


class DisplayMode(str, Enum):
    """Transcript visual presentation modes."""
    ORIGINAL_ONLY = "original_only"
    TRANSLATION_ONLY = "translation_only"
    BOTH = "both"


class ThemeMode(str, Enum):
    """Supported UI color themes."""
    DARK = "dark"
    LIGHT = "light"


SUPPORTED_LANGUAGES: dict[str, str] = {
    "auto": "Auto-Detect",
    "en": "English",
    "ta": "Tamil (தமிழ்)",
    "hi": "Hindi (हिन्दी)",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "ja": "Japanese",
    "zh": "Chinese",
}

AVAILABLE_MODELS: list[str] = [
    "tiny",
    "base",
    "small",
    "medium",
    "large-v3",
]
