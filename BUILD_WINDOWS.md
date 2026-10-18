# Building Live Transcript for Windows

This document describes how to produce a standalone Windows executable for
Live Transcript v0.1.0 using PyInstaller.

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.10.x (must match the `.venv`) |
| Windows | 10 or 11 (64-bit) |
| Disk space | ≥ 3 GB free (build artefacts + dependencies) |

All Python dependencies must already be installed in `.venv`.
Run the setup script if the venv is missing:

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

---

## Quick Build

From the project root:

```powershell
.\scripts\build_windows.ps1
```

This will:
1. Verify `.venv` exists.
2. Run all 44 unit/integration tests. Build aborts on test failure.
3. Run PyInstaller with `live_transcript.spec`.
4. Report the output size and list top-level dist files.

To skip tests (e.g. for a fast rebuild after a minor change):

```powershell
.\scripts\build_windows.ps1 -SkipTests
```

---

## Manual Build

```powershell
.\.venv\Scripts\pyinstaller.exe live_transcript.spec --clean --noconfirm
```

Output is written to `dist\LiveTranscript\`.

---

## Output Structure

```
dist\
└── LiveTranscript\
    ├── LiveTranscript.exe          # Main executable (17–18 MB)
    └── _internal\                  # All dependencies
        ├── ctranslate2.dll         # CTranslate2 inference engine (56 MB)
        ├── onnxruntime.dll         # ONNX Runtime (15 MB)
        ├── cudnn64_9.dll           # cuDNN (GPU, optional)
        ├── libiomp5md.dll          # Intel OpenMP runtime
        ├── python310.dll           # Python runtime
        ├── PySide6\                # Qt6 libraries + plugins
        │   └── plugins\
        │       ├── platforms\qwindows.dll
        │       ├── styles\
        │       └── imageformats\
        ├── faster_whisper\
        │   └── assets\silero_vad_v6.onnx   # VAD model
        ├── soundcard\              # Windows WASAPI backend (mediafoundation.py)
        ├── tokenizers.pyd          # HuggingFace tokenizer C extension
        └── assets\
            ├── icon.ico
            └── icon.png
```

**Total dist size: ~976 MB**
**Executable size: ~17.5 MB**

---

## User Data

The packaged application stores all persistent data in:

```
%LOCALAPPDATA%\LiveTranscript\
├── live_transcript.db      # SQLite database (sessions, vocabulary, settings)
├── logs\live_transcript.log
├── models\                 # Whisper model weights (downloaded on first use)
│   └── models--Systran--faster-whisper-base\
├── exports\
└── backups\
```

> **Important:** The packaged executable does NOT touch or overwrite the
> developer's database at `%LOCALAPPDATA%\LiveTranscript\live_transcript.db`.
> Both the `app.py` development launcher and `LiveTranscript.exe` share the
> same data directory, so existing sessions and vocabulary are visible
> immediately in the packaged build.

---

## Whisper Model Download

Model weights are **not** bundled in the executable (they are 75 MB–1.5 GB
depending on the selected model size). On the first click of **Start**:

1. The app checks `%LOCALAPPDATA%\LiveTranscript\models\` for the selected model.
2. If not found, `ModelDownloadDialog` opens and downloads it from HuggingFace Hub.
3. The `base` model (~145 MB) is recommended and takes roughly 1–3 minutes on
   a typical broadband connection.

If the model was already downloaded during development (the common case), the
packaged app finds it immediately — no re-download is required.

---

## Verification Checklist

After building, verify the following manually:

- [ ] `dist\LiveTranscript\LiveTranscript.exe` exists and is ≥ 15 MB
- [ ] Double-click the exe — the dark-themed window opens without errors
- [ ] Navigate to **Settings** and confirm the model selector shows Tiny/Base/Small/Medium
- [ ] Click **Start** — if the base model is cached, transcription begins immediately
- [ ] Play audio through system speakers — the audio meter responds
- [ ] Recognized speech appears as transcript cards
- [ ] Navigate to **History** — previous sessions from `app.py` are visible
- [ ] Navigate to **Vocabulary** — existing words are preserved
- [ ] Close and reopen the exe — the database persists correctly

---

## Build Warnings (Safe to Ignore)

| Warning | Reason | Impact |
|---------|--------|--------|
| `fbclient.dll not found` | Firebird SQL driver (Qt optional plugin) | None — we use SQLite |
| `MIMAPI64.dll not found` | Mimer SQL driver (Qt optional plugin) | None |
| `OCI.dll not found` | Oracle SQL driver (Qt optional plugin) | None |
| `LIBPQ.dll not found` | PostgreSQL SQL driver (Qt optional plugin) | None |
| `pycparser.lextab not found` | Optional pre-generated parse table | None |
| `scipy.special._cdflib not found` | Optional Cython extension | None |

These warnings originate from `collect_all("PySide6")` gathering every Qt SQL
driver plugin regardless of whether the database server is installed. They do
not affect functionality.

---

## Rebuilding After Code Changes

No need to reinstall dependencies. Just re-run PyInstaller:

```powershell
.\.venv\Scripts\pyinstaller.exe live_transcript.spec --clean --noconfirm
```

Or use the build script (runs tests automatically):

```powershell
.\scripts\build_windows.ps1
```

---

## Known Limitations

| Limitation | Details |
|-----------|---------|
| Windows only | The spec and WASAPI audio capture are Windows-specific |
| ~976 MB dist folder | PySide6 + ctranslate2 are large; no easy way to trim without removing features |
| GPU requires cuDNN | `cudnn64_9.dll` is bundled but CUDA drivers must be installed by the user |
| No auto-update | Updates require a new build and manual distribution |
| No code-signing | The executable is unsigned; Windows SmartScreen may warn on first launch |

---

## Phase Roadmap

This build completes **Phase 1** of the release roadmap. See
[RELEASE_ROADMAP.md](RELEASE_ROADMAP.md) for the full 10-phase plan.

Next phases:
- **Phase 2:** Inno Setup installer (one-click install, Start Menu, uninstaller)
- **Phase 3:** Code signing with a certificate
- **Phase 4:** Auto-update mechanism
- **Phase 5:** Public website and download page
