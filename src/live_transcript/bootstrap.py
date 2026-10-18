"""Application bootstrap, environment setup, and lifecycle initialization."""

import argparse
import sys
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from live_transcript.config import AppConfig, load_config
from live_transcript.database.connection import DatabaseConnection
from live_transcript.database.migrations import MigrationRunner
from live_transcript.ui.main_window import MainWindow
from live_transcript.utils.logging_setup import get_logger, setup_logging

logger = get_logger("bootstrap")


def bootstrap_environment(config: Optional[AppConfig] = None) -> tuple[AppConfig, DatabaseConnection]:
    """Bootstrap configuration, logging, and database migrations."""
    cfg = config or load_config()

    # 1. Initialize logging
    setup_logging(log_dir=cfg.log_dir, log_level=cfg.log_level)
    logger.info("Starting Live Transcript application bootstrap...")

    # 2. Initialize Database and run migrations
    db = DatabaseConnection(cfg.db_path)
    runner = MigrationRunner(db)
    runner.run_migrations()
    logger.info("Database bootstrap completed at: %s", cfg.db_path)

    return cfg, db


def main() -> int:
    """Application CLI and GUI entry point."""
    parser = argparse.ArgumentParser(description="Live Transcript Desktop Application")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Initialize configuration, database, and logging without opening the GUI window.",
    )
    args = parser.parse_args()

    # 1. Bootstrap backend services
    config, db = bootstrap_environment()

    if args.dry_run:
        logger.info("Dry-run bootstrap completed successfully. Exiting without launching GUI.")
        return 0

    # 2. Enable High DPI and instantiate Qt Application
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Set Windows AppUserModelID so taskbar displays custom icon
    import ctypes
    from live_transcript.utils.platform_utils import is_windows, get_resource_path
    from PySide6.QtGui import QIcon

    if is_windows():
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("LiveTranscript.Desktop.App")
        except Exception as exc:
            logger.debug("Could not set AppUserModelID: %s", exc)

    app = QApplication(sys.argv)
    app.setApplicationName("Live Transcript")
    app.setOrganizationName("LiveTranscript")

    # Set global application icon
    icon_path = get_resource_path("assets/icon.ico")
    if not icon_path.exists():
        icon_path = get_resource_path("assets/icon.png")
    if icon_path.exists():
        app_icon = QIcon(str(icon_path))
        app.setWindowIcon(app_icon)
    else:
        app_icon = None

    # 3. Instantiate and show main window
    window = MainWindow(config=config, db=db)
    if app_icon:
        window.setWindowIcon(app_icon)
    window.show()

    logger.info("Entering Qt event loop...")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
