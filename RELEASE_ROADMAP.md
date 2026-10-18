# Live Transcript — Production Release & Cross-Platform Roadmap

## Executive Summary
**Live Transcript** is a local-first, privacy-respecting desktop application designed to transcribe, translate, and aid in language learning from system audio playback (videos, meetings, podcasts, reels) and microphone inputs. 

This document outlines the product release roadmap, target distribution architectures across Windows, Android, and iOS, technical risks, security/privacy boundaries, and phased acceptance criteria.

---

## 1. System Architecture

### 1.1 Current Desktop Architecture (v0.1.0)
```
┌────────────────────────────────────────────────────────────────────────┐
│                        Live Transcript Desktop                         │
├────────────────────────────────────────────────────────────────────────┤
│  PySide6 (Qt6) Presentation Layer                                      │
│  ├── DashboardView, LiveTranscriptView, HistoryView, VocabularyView    │
│  ├── TranscriptEditorWidget (QPlainTextEdit with timestamp regex)      │
│  └── AudioLevelMeter, StatusBadge, WordLookupDialog                    │
├────────────────────────────────────────────────────────────────────────┤
│  Domain & Pipeline Layer (Asynchronous / Non-blocking)                 │
│  ├── AudioCaptureService (WASAPI Loopback via SoundCard, 48kHz stereo) │
│  ├── AudioPreprocessor (Resampling 16kHz, mono conversion, RMS meter)  │
│  ├── BoundedAudioQueue & ChunkAccumulator (thread-safe, zero leaks)    │
│  ├── TranscriptionPipeline & TranscriptionWorker (QThread/threading)   │
│  └── LocalWhisperProvider (Faster-Whisper / CTranslate2 CPU/CUDA)      │
├────────────────────────────────────────────────────────────────────────┤
│  Persistence & Services Layer                                          │
│  ├── SQLite Database (%LOCALAPPDATA%/LiveTranscript/live_transcript.db)│
│  │   ├── WAL Mode, Foreign Keys, Schema Migrations                     │
│  │   └── Repositories: Session, Segment, Vocabulary, Settings          │
│  ├── DictionaryService (Free Dictionary API + Offline Lexicon)         │
│  └── AppConfig (%LOCALAPPDATA%/LiveTranscript, AppData Isolation)       │
└────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Target Production Windows Distribution Architecture
```
┌────────────────────────────────────────────────────────────────────────┐
│                    Windows Packaged Release (v0.2.0+)                  │
├────────────────────────────────────────────────────────────────────────┤
│  Distribution Artifacts                                                │
│  ├── LiveTranscript-Setup-x64.exe (Inno Setup / WiX Installer)         │
│  │   ├── Desktop Shortcut, Start Menu Shortcut, Add/Remove Programs   │
│  │   └── Auto-run on Startup Toggle (Registry HKCU\...\Run)            │
│  └── LiveTranscript-Portable-x64.zip (Standalone directory)            │
├────────────────────────────────────────────────────────────────────────┤
│  Packaged Runtime (PyInstaller onedir distribution)                    │
│  ├── LiveTranscript.exe (WinMain GUI subsystem, no console window)     │
│  ├── Single-Instance Guard (Windows Named Mutex / Local Socket)        │
│  ├── Global Hotkey Manager (Win32 RegisterHotKey API)                  │
│  ├── System Tray Manager (QSystemTrayIcon + Quick Actions)             │
│  ├── First-Run Model Downloader (Progress dialog + Disk space check)   │
│  └── Bundled CTranslate2, ONNX, PySide6 Qt binaries & assets           │
├────────────────────────────────────────────────────────────────────────┤
│  User Data & Migration Isolation                                       │
│  ├── %LOCALAPPDATA%/LiveTranscript/live_transcript.db (Survives update)│
│  ├── %LOCALAPPDATA%/LiveTranscript/models/ (Shared model cache)        │
│  └── %LOCALAPPDATA%/LiveTranscript/logs/ (Rotating file logs)          │
└────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Target Mobile Architecture (Android & iOS)
Due to mobile operating system sandboxing:
- **Desktop** can capture arbitrary system audio via Windows WASAPI loopback.
- **Android (API 29+)** strictly restricts third-party audio capture: apps can only capture audio from other apps if those apps explicitly opted in with `AudioAttributes.USAGE_MEDIA` and `USAGE_GAME` via `AudioPlaybackCaptureConfiguration`, or via `MediaProjection` (which requires screen recording consent and notification prompts).
- **iOS** sandbox completely forbids inter-app audio sniffing. Third-party apps cannot record audio played by YouTube, Instagram, or Safari.
- Therefore, the mobile architecture is designed as an **Audio-First Companion Client**:
  1. Live microphone speech transcription (lectures, in-person meetings, conversations).
  2. Audio/Video file import and transcription (downloaded podcasts, lecture recordings, voicemails).
  3. Shared vocabulary review, flashcards, and transcript study.
  4. Local-first transcription using Whisper Mobile (Whisper.cpp / ONNX Mobile / TFLite) or native Speech APIs (`SFSpeechRecognizer` / `Android SpeechRecognizer`).

```
┌────────────────────────────────────────────────────────────────────────┐
│                      Mobile Client (Flutter / Dart)                    │
├────────────────────────────────────────────────────────────────────────┤
│  Presentation Layer (Material 3 / Cupertino Adaptive UI)               │
│  ├── Live Audio View (Microphone input + waveforms)                    │
│  ├── File Import & Transcribe View                                     │
│  ├── History & Transcript Reader View                                  │
│  └── Vocabulary & Study Cards View                                     │
├────────────────────────────────────────────────────────────────────────┤
│  Mobile Engine Interfaces (Platform Channels)                          │
│  ├── Android: AudioRecord API + MediaProjection fallback               │
│  ├── iOS: AVAudioEngine + SFSpeechRecognizer / whisper.cpp             │
│  ├── Local Inference: whisper.cpp / onnxruntime-mobile                 │
│  └── Local Database: SQLite (sqflite / Drift) matching schema          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Phased Implementation Roadmap

### Phase 1 — Windows Desktop Release Packaging
- **Objective**: Package the existing Python application as a standalone, production-grade Windows desktop application with zero external Python dependency.
- **Key Tasks**:
  1. Set up PyInstaller packaging pipeline with reproducible `live_transcript.spec`.
  2. Implement High-DPI application icon (`assets/icon.ico` and PNG variants).
  3. Implement first-run model manager dialog in UI with disk-space verification (ensuring >= 1 GB free before downloading `base` or `tiny`), progress percentage, and cancel/retry support.
  4. Ensure user database and logs remain in `%LOCALAPPDATA%\LiveTranscript` so upgrades never overwrite user history.
  5. Build automated Windows packaging script `scripts/build_windows.py` and `scripts/build_installer.iss` (Inno Setup).
- **Acceptance Criteria**:
  - `LiveTranscript.exe` starts without a console prompt on a clean Windows machine without Python.
  - Faster-Whisper, SoundCard WASAPI loopback, and SQLite persist correctly.
  - Automated tests pass on packaged distribution.

### Phase 2 — Desktop Shortcut, Start Menu & Global Hotkey
- **Objective**: Convenient system launching, single-instance enforcement, and system-wide visibility toggle.
- **Key Tasks**:
  1. Implement single-instance lock using a Windows Named Mutex (`Global\LiveTranscript_Instance_Mutex`) with window restore on duplicate launch.
  2. Implement global keyboard hotkey registration using Win32 `RegisterHotKey` (e.g. `Ctrl+Alt+T` or `Win+Alt+T`) without invasive keyboard hooks.
  3. Add shortcut configuration and conflict detection in Settings View.
  4. Create Start Menu and Desktop shortcut configurations in installer.
- **Acceptance Criteria**:
  - Pressing the hotkey toggles application minimize/restore from anywhere in Windows.
  - Duplicate launch focuses existing instance instead of opening a second window.

### Phase 3 — Background Operation & Quick Capture
- **Objective**: System-tray integration and privacy-respecting background capture.
- **Key Tasks**:
  1. Integrate `QSystemTrayIcon` with contextual menu (Show, Hide, Start Capture, Stop Capture, Exit).
  2. Implement minimize-to-tray and close-to-tray user settings.
  3. Ensure no audio is recorded without explicit user initiation; provide clear visual badge when recording.
  4. Cleanly release audio streams and worker threads upon Exit.
- **Acceptance Criteria**:
  - Closing window minimizes to tray if configured.
  - Audio capture and speech recognition start only on user demand.
  - Clean resource release on shutdown.

### Phase 4 — Public Website and Distribution
- **Objective**: Professional product landing page, downloads, documentation, and release integrity.
- **Key Tasks**:
  1. Design modern, accessible static landing page (HTML5/Tailwind/CSS) with dark aesthetic matching the app.
  2. Add product screenshots, system requirements, Windows installation guide, FAQ, and privacy pledge.
  3. Generate SHA-256 checksums and release metadata for distribution binaries.
  4. Configure GitHub Pages / Cloudflare Pages deployment workflow.
- **Acceptance Criteria**:
  - Responsive, fast, HTTPS-ready static site.
  - Clear distinction between desktop system-audio features and mobile capabilities.

### Phase 5 — Android Application
- **Objective**: Android companion application for microphone transcription, audio file import, and vocabulary study.
- **Key Tasks**:
  1. Scaffold Flutter Android project sharing design language and data structures.
  2. Implement microphone speech capture with permission handling.
  3. Integrate on-device transcription engine (Whisper.tflite / Sherpa-ONNX).
  4. Local SQLite database matching desktop schema.
- **Acceptance Criteria**:
  - Compiles and runs on Android 10+ (API 29+).
  - Transcribes live speech from microphone offline.

### Phase 6 — iOS Application
- **Objective**: Native or Flutter iOS companion application adhering to Apple privacy guidelines.
- **Key Tasks**:
  1. Configure iOS build target, permissions (`NSMicrophoneUsageDescription`, `NSSpeechRecognitionUsageDescription`).
  2. Implement AVAudioSession lifecycle and on-device transcription via whisper.cpp or Apple Speech.
  3. Share transcript and vocabulary management workflows.
- **Acceptance Criteria**:
  - Builds in Xcode, runs on iOS 16+ simulator and physical test devices.
  - Compliant with App Store privacy requirements.

### Phase 7 — Shared Mobile Architecture & Data Model
- **Objective**: Unified Flutter codebase for Android and iOS with clean separation of platform audio and inference.
- **Key Tasks**:
  1. Shared repository and domain services.
  2. Standardized JSON/SQLite import-export format between desktop and mobile.
- **Acceptance Criteria**:
  - Desktop export files can be imported into mobile without loss of timestamps or vocabulary.

### Phase 8 — Optional Privacy-First Cloud Synchronization
- **Objective**: End-to-end encrypted synchronization across devices without mandatory user accounts.
- **Key Tasks**:
  1. Design zero-knowledge sync protocol (client-side AES-GCM encryption before sync).
  2. Support self-hosted WebDAV / cloud drive sync (Google Drive, Nextcloud) as user-owned storage.
- **Acceptance Criteria**:
  - Fully optional; app remains 100% functional offline without cloud credentials.

### Phase 9 — Quality Assurance & Release Automation
- **Objective**: Robust automated testing, packaging verification, and release checklists.
- **Key Tasks**:
  1. GitHub Actions workflow matrix for Windows build, linting, and pytest suites.
  2. Automatic SHA-256 manifest generation.
  3. Release artifact sanity check scripts.
- **Acceptance Criteria**:
  - Automated CI completes green on all commits and tags.

### Phase 10 — Production Documentation
- **Objective**: Exhaustive technical and user-facing documentation.
- **Key Tasks**:
  - Update `README.md`, `BUILD_WINDOWS.md`, `BUILD_ANDROID.md`, `BUILD_IOS.md`, `PRIVACY.md`, `CHANGELOG.md`, `CONTRIBUTING.md`.
- **Acceptance Criteria**:
  - Anyone can clone the repository and reproduce the builds following the docs.

---

## 3. Technical Risks & Mitigations

| Risk | Impact | Mitigation Strategy |
|---|---|---|
| Large model binaries (>150 MB) in installer | Bloated installer download | Bundle zero models in installer; provide interactive first-run downloader with disk check and progress bar. |
| Missing PySide6 Qt plugins or CTranslate2 DLLs in executable | Packaged app fails on clean Windows | Custom PyInstaller hook collecting CTranslate2 DLLs, ONNX runtime, and Qt plugins with verification test. |
| Global hotkey conflict with Windows shortcuts | Registration failure | Catch registration errors gracefully, provide user notification, and allow user-customized keys in Settings. |
| Operating system restrictions on mobile system audio | Users expect mobile to record other apps like Instagram/YouTube | Clear in-app and website documentation clarifying desktop loopback vs mobile microphone/file transcription. |
| Multi-instance database locks on SQLite | Database locking errors | Windows named mutex ensuring only one application instance runs at a time. |

---

## 4. Acceptance Criteria for Phase 1 (Windows Desktop Release)
1. PyInstaller spec file bundles all runtime dependencies, PySide6 plugins, CTranslate2, and assets.
2. Executable starts cleanly without requiring Python on Windows.
3. First-run model download verifies free disk space and displays progress.
4. User database in `%LOCALAPPDATA%\LiveTranscript` is preserved across builds.
5. Automated test suite runs and passes against the codebase.
