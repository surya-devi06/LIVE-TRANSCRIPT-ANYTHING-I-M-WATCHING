# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Live Transcript v0.1.0
# Build with: pyinstaller live_transcript.spec --clean --noconfirm
#
# Architecture notes:
#   - onedir mode (not onefile) avoids slow extraction on each launch
#   - Models are NOT bundled; they download on first use to %LOCALAPPDATA%\LiveTranscript\models\
#   - Native DLLs for ctranslate2, onnxruntime, tokenizers are explicitly collected
#   - soundcard uses its own __pyinstaller hook directory which PyInstaller finds automatically
#   - PySide6 plugins (platform, styles, imageformats, multimedia) are fully collected

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_dynamic_libs

# ── Paths ──────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(SPECPATH)          # directory containing this .spec file
SRC_DIR      = PROJECT_ROOT / "src"

# ── Collect packages with native extensions ───────────────────────────────────
# collect_all returns (datas, binaries, hiddenimports)
ct2_datas,    ct2_bins,    ct2_hiddens    = collect_all("ctranslate2")
fw_datas,     fw_bins,     fw_hiddens     = collect_all("faster_whisper")
sc_datas,     sc_bins,     sc_hiddens     = collect_all("soundcard")
ort_datas,    ort_bins,    ort_hiddens    = collect_all("onnxruntime")
tok_datas,    tok_bins,    tok_hiddens    = collect_all("tokenizers")
pyside_datas, pyside_bins, pyside_hiddens = collect_all("PySide6")

# ── Application datas ─────────────────────────────────────────────────────────
app_datas = [
    # (source, destination_inside_bundle)
    (str(PROJECT_ROOT / "assets"), "assets"),
]

all_datas = (
    app_datas
    + ct2_datas
    + fw_datas
    + sc_datas
    + ort_datas
    + tok_datas
    + pyside_datas
)

all_binaries = (
    ct2_bins
    + fw_bins
    + sc_bins
    + ort_bins
    + tok_bins
    + pyside_bins
)

all_hiddenimports = list(set(
    ct2_hiddens
    + fw_hiddens
    + sc_hiddens
    + ort_hiddens
    + tok_hiddens
    + pyside_hiddens
    + [
        # Application modules that PyInstaller may miss due to dynamic imports
        "live_transcript.bootstrap",
        "live_transcript.config",
        "live_transcript.database.connection",
        "live_transcript.database.migrations",
        "live_transcript.database.repositories",
        "live_transcript.database.models",
        "live_transcript.audio.capture",
        "live_transcript.audio.buffer",
        "live_transcript.transcription.base",
        "live_transcript.transcription.local_whisper",
        "live_transcript.transcription.pipeline",
        "live_transcript.transcription.worker",
        "live_transcript.transcription.model_manager",
        "live_transcript.ui.main_window",
        "live_transcript.ui.styles",
        "live_transcript.ui.dialogs",
        "live_transcript.ui.dialogs.word_lookup_dialog",
        "live_transcript.ui.dialogs.model_download_dialog",
        "live_transcript.ui.views.dashboard",
        "live_transcript.ui.views.live_transcript",
        "live_transcript.ui.views.history_view",
        "live_transcript.ui.views.settings_view",
        "live_transcript.ui.views.vocabulary_view",
        "live_transcript.ui.views.about_view",
        "live_transcript.ui.widgets.audio_meter",
        "live_transcript.ui.widgets.status_badge",
        "live_transcript.ui.widgets.transcript_editor",
        "live_transcript.services.dictionary_service",
        "live_transcript.utils.platform_utils",
        "live_transcript.utils.logging_setup",
        # Standard-library / third-party hidden deps
        "scipy.signal",
        "scipy.signal.windows",
        "scipy.fft",
        "numpy",
        "numpy.core._multiarray_umath",
        "numpy.fft",
        "ctypes",
        "ctypes.util",
        "threading",
        "queue",
        "sqlite3",
        "json",
        "pathlib",
        "dataclasses",
        "typing_extensions",
    ]
))

# ── Analysis ──────────────────────────────────────────────────────────────────
a = Analysis(
    [str(PROJECT_ROOT / "app.py")],
    pathex=[
        str(PROJECT_ROOT),
        str(SRC_DIR),               # so 'live_transcript' package is found
    ],
    binaries=all_binaries,
    datas=all_datas,
    hiddenimports=all_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude heavy optional deps not used at runtime
        "torch",
        "torchvision",
        "torchaudio",
        "matplotlib",
        "IPython",
        "jupyter",
        "notebook",
        "tkinter",
        "_tkinter",
        "PIL",           # Pillow — not needed at runtime
        "cv2",
        "sklearn",
        "pandas",
    ],
    noarchive=False,
    optimize=0,
)

# ── PYZ (Python bytecode archive) ─────────────────────────────────────────────
pyz = PYZ(a.pure)

# ── EXE ──────────────────────────────────────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,          # onedir mode: binaries go into COLLECT
    name="LiveTranscript",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                      # UPX can break some DLLs; leave off
    console=False,                  # No console window (windowed app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(PROJECT_ROOT / "assets" / "icon.ico"),
    version_file=None,
)

# ── COLLECT (assemble the onedir dist folder) ─────────────────────────────────
# ── ONE‑FILE EXE ────────────────────────────────────────────────────────
onefile = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="LiveTranscript",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=str(PROJECT_ROOT / "assets" / "icon.ico"),
)
