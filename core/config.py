"""Application configuration and constants."""

import os
import sys
from pathlib import Path

# Execution environment detection: frozen exe (PyInstaller) vs development
IS_FROZEN = getattr(sys, "frozen", False)

if IS_FROZEN:
    BASE_DIR = Path(sys.executable).parent
    ASSETS_DIR = Path(getattr(sys, "_MEIPASS", BASE_DIR)) / "assets"
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    ASSETS_DIR = BASE_DIR / "assets"

# User persistent data directory
if sys.platform == "win32":
    APP_DATA_DIR = Path(os.environ.get("APPDATA", Path.home())) / "LumieTL"
else:
    APP_DATA_DIR = Path.home() / ".lumietl"

MODEL_DIR = APP_DATA_DIR / "models"
HISTORY_DB = APP_DATA_DIR / "history.db"
SETTINGS_FILE = APP_DATA_DIR / "settings.enc"
KEYS_FILE = APP_DATA_DIR / "keys.enc"
LOG_FILE = APP_DATA_DIR / "app.log"
OUTPUT_DIR = APP_DATA_DIR / "output"

# Application metadata
APP_NAME = "LumieTL"
APP_VERSION = "1.0.0"

# File & processing constraints
MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MAX_IMAGE_DIMENSION = 8192
MAX_IMAGE_PIXELS = 67_108_864  # 64 MegaPixels safety threshold against decompression bombs
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}

# Supported languages
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

# Translation engines
TRANSLATOR_ENGINES: dict[str, str] = {
    "google": "Google Translate",
    "deepl": "DeepL",
    "openai": "OpenAI GPT-4o",
}

# Default UI color tokens
COLORS = {
    "bg_base": "#0F0F11",
    "bg_surface": "#18181C",
    "bg_elevated": "#222228",
    "border": "#2A2A30",
    "text_primary": "#E8E8ED",
    "text_secondary": "#8A8A96",
    "accent": "#6C8EF5",
    "success": "#4CAF82",
    "error": "#E05C5C",
    "warning": "#D4A847",
}

# Web server settings
WEB_PORT = int(os.environ.get("LUMIETL_PORT", 18420))
WEB_HOST = os.environ.get("LUMIETL_HOST", "127.0.0.1")
WEB_AUTH_ENABLED = os.environ.get("LUMIETL_AUTH_ENABLED", "false").lower() == "true"
WEB_AUTH_USER = os.environ.get("LUMIETL_AUTH_USER", "admin")
WEB_AUTH_PASS = os.environ.get("LUMIETL_AUTH_PASS", "")


def ensure_directories():
    """Ensure that runtime data directories exist."""
    for directory in [APP_DATA_DIR, MODEL_DIR, OUTPUT_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
