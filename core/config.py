"""Application constants, paths, and configuration values."""

import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Data directories — persist between restarts
# ---------------------------------------------------------------------------
if sys.platform == "win32":
    _base = Path(os.environ.get("APPDATA", Path.home()))
else:
    _base = Path.home()

APP_DATA_DIR: Path = _base / "LumieTL"
MODEL_DIR: Path = APP_DATA_DIR / "models"
HISTORY_DB: Path = APP_DATA_DIR / "history.db"
SETTINGS_FILE: Path = APP_DATA_DIR / "settings.enc"
KEYS_FILE: Path = APP_DATA_DIR / "keys.enc"
LOG_FILE: Path = APP_DATA_DIR / "app.log"
OUTPUT_DIR: Path = APP_DATA_DIR / "output"

# ---------------------------------------------------------------------------
# App metadata
# ---------------------------------------------------------------------------
APP_NAME: str = "LumieTL"
APP_VERSION: str = "1.0.0"

# ---------------------------------------------------------------------------
# File constraints
# ---------------------------------------------------------------------------
MAX_FILE_SIZE_MB: int = 500
MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".webp", ".avif"}

# ---------------------------------------------------------------------------
# Supported languages
# ---------------------------------------------------------------------------
SOURCE_LANGS: dict[str, str] = {
    "auto": "Auto-detect",
    "JPN": "Jepang",
    "KOR": "Korea",
    "CHS": "Mandarin (Simplified)",
    "CHT": "Mandarin (Traditional)",
}

TARGET_LANGS: dict[str, str] = {
    "ID": "Indonesia",
    "EN": "Inggris",
    "VI": "Vietnam",
    "TH": "Thailand",
}

# ---------------------------------------------------------------------------
# Translation engines
# ---------------------------------------------------------------------------
TRANSLATOR_ENGINES: dict[str, str] = {
    "google": "Google Translate",
    "deepl": "DeepL",
    "openai": "OpenAI GPT-4o",
}

# Engine-specific rate limits (requests per window)
ENGINE_RATE_LIMITS: dict[str, dict[str, int]] = {
    "google": {"max_requests": 30, "window_seconds": 60},
    "deepl": {"max_requests": 50, "window_seconds": 60},
    "openai": {"max_requests": 20, "window_seconds": 60},
}

# ---------------------------------------------------------------------------
# Web server configuration (via environment variables)
# ---------------------------------------------------------------------------
WEB_PORT: int = int(os.environ.get("LUMIETL_PORT", "18420"))
WEB_AUTH_ENABLED: bool = (
    os.environ.get("LUMIETL_AUTH_ENABLED", "false").lower() == "true"
)
WEB_AUTH_USER: str = os.environ.get("LUMIETL_AUTH_USER", "admin")
WEB_AUTH_PASS: str = os.environ.get("LUMIETL_AUTH_PASS", "")

# ---------------------------------------------------------------------------
# Concurrent processing
# ---------------------------------------------------------------------------
MAX_CONCURRENT_TRANSLATIONS: int = 3
