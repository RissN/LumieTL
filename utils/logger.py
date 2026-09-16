"""Logging setup and structured audit function."""

import logging
from pathlib import Path

from core.config import LOG_FILE


def _setup() -> logging.Logger:
    """Create and configure the application logger."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    app_logger = logging.getLogger("lumietl")
    app_logger.setLevel(logging.INFO)

    # Avoid duplicate handlers on reload
    if not app_logger.handlers:
        file_handler = logging.FileHandler(str(LOG_FILE), encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        app_logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(message)s",
                datefmt="%H:%M:%S",
            )
        )
        app_logger.addHandler(console_handler)

    return app_logger


logger: logging.Logger = _setup()


def audit(action: str, detail: str = "") -> None:
    """Write a structured audit log entry.

    Usage::

        audit("translate_start", "engine=google source=JPN file=ch01.jpg")
        audit("translate_done", "duration=2.3s")
        audit("api_key_saved", "provider=deepl")
    """
    logger.info("AUDIT | %s | %s", action, detail)
