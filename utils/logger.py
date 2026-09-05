"""Application logging configuration with rotating file handler."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from core.config import LOG_FILE, APP_DATA_DIR

_logger: logging.Logger | None = None


def setup_logger(name: str = "LumieTL", level: int = logging.INFO) -> logging.Logger:
    """Set up and configure the application logger."""
    global _logger
    if _logger is not None:
        return _logger

    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers if re-called
    if not logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Rotating file handler (max 10 MB per file, keep 3 backups)
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=10 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        logger.addHandler(console_handler)

    _logger = logger
    return logger


def get_logger() -> logging.Logger:
    """Retrieve the shared application logger instance."""
    if _logger is None:
        return setup_logger()
    return _logger
