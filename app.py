"""Executable root entry point for the Live Transcript application."""

import sys
from pathlib import Path

# Ensure 'src' directory is in sys.path when running as a direct script
SRC_PATH = Path(__file__).resolve().parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from live_transcript.bootstrap import main

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
        sys.exit(0)
    except Exception as exc:
        print(f"Fatal error during application launch: {exc}", file=sys.stderr)
        sys.exit(1)
