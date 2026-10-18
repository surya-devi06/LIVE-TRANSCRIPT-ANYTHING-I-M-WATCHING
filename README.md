 # Live Transcript: Real-Time AI Audio Transcription Desktop App

A modern, high-performance Windows desktop application designed to transcribe speech from anything you are watching or listening to on your computer in real-time (Instagram Reels, YouTube videos, online courses, podcasts, meetings) using Windows WASAPI loopback capture, local Faster-Whisper, and AI assistance.

---

## Features (Phase 1: Project Foundation)

- **Modern Desktop UI:** Built on PySide6 (Qt 6) with customizable dark and light themes, responsive layouts, and accessible contrast.
- **Persistent Local SQLite Storage:** Session metadata, transcript segments, saved vocabulary, and user preferences stored with WAL (Write-Ahead Logging) and versioned schema migrations.
- **Robust Architecture:** Clean separation of concerns between UI components and domain repositories.
- **Structured Logging:** Rotating log files with automatic secret masking.
- **Windows High-DPI Support:** Native crisp rendering on high-resolution displays.

---

## Prerequisites

- **Operating System:** Windows 11 (64-bit) or Windows 10 (64-bit).
- **Python Version:** Python 3.10 (64-bit) recommended.
- **Hardware Acceleration (Optional):** NVIDIA GPU with CUDA support for accelerated local speech recognition.

---

## Quick Start (Windows 11 PowerShell)

### 1. Setup Virtual Environment and Dependencies
Open PowerShell in the project directory and run:

```powershell
# Create virtual environment
py -3.10 -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Alternatively, run the automated setup script:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup_dev.ps1
```

### 2. Run the Application
```powershell
# Run using the virtual environment
.\.venv\Scripts\python.exe app.py
```
Or via the run script:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_dev.ps1
```

### 3. Run Automated Unit Tests
```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit -v
```

---

## Architecture Overview

```
LIVE TRANSCRIPT ANYTHING I'M WATCHING/
├── app.py                      # Application executable entry point
├── pyproject.toml              # Build & dependency packaging
├── requirements.txt            # Python dependencies
├── src/live_transcript/
│   ├── bootstrap.py            # App lifecycle, DPI awareness & initialization
│   ├── config.py               # Settings & path management
│   ├── constants.py            # Application enums & constants
│   ├── database/
│   │   ├── connection.py       # Thread-safe SQLite connection with WAL
│   │   ├── migrations.py       # Versioned migration runner (V1 initial schema)
│   │   ├── models.py           # Dataclass models (Session, Segment, Vocab)
│   │   └── repositories.py     # Parameterized SQL CRUD operations
│   ├── ui/
│   │   ├── main_window.py      # Main window with sidebar navigation
│   │   ├── styles.py           # Modern Dark & Light QSS theme stylesheets
│   │   ├── views/              # Dashboard, Live Transcript, History, Vocab, Settings, About
│   │   └── widgets/            # Custom reusable UI widgets (StatusBadge, etc.)
│   └── utils/
│       ├── logging_setup.py    # Rotating file logging & secret masking
│       └── platform_utils.py   # Windows path & directory helpers
└── tests/                      # Automated unit test suite
```

---

## Project Roadmap

- **Phase 1: Project Foundation** *(Current)* - UI shell, SQLite migrations, configuration, logging, and unit tests.
- **Phase 2: System Audio Capture** - Windows WASAPI loopback audio capture, buffer management, and resampling.
- **Phase 3: Local Speech Recognition** - Faster-Whisper integration, background worker threads, and live transcript streaming.
- **Phase 4: Transcript Management** - Session persistence, subtitle exports (SRT, VTT, TXT, JSON), and search.
- **Phase 5: Translation Engine** - Multilingual translation (Tamil, Hindi, English) with asynchronous queuing.
- **Phase 6: AI Language Learning** - Contextual grammar explanations and vocabulary builder.
- **Phase 7: Global Hotkeys & Floating Overlay** - Always-on-top compact overlay and Windows hotkeys.
- **Phase 8: Reliability & Performance** - Backpressure control, bounded queues, and device-loss recovery.
- **Phase 9: Packaging & Release** - Windows standalone executable build.
