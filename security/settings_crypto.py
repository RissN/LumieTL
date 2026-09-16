"""Encryption utilities for application settings.

Generates a random Fernet key on first run and stores it in a file
with restricted permissions (600). The key is NOT derived from any
hardware identifier — it is purely random.
"""

import base64
import json
import os
import stat
from pathlib import Path

from cryptography.fernet import Fernet

from core.config import APP_DATA_DIR

_KEY_FILE: Path = APP_DATA_DIR / ".app_key"


def get_or_create_app_key() -> bytes:
    """Return the app encryption key, creating one on first run.

    The key is stored as url-safe base64 in a file readable only by
    the owner (chmod 600 on Linux, best-effort on Windows).
    """
    _KEY_FILE.parent.mkdir(parents=True, exist_ok=True)

    if _KEY_FILE.exists():
        raw = _KEY_FILE.read_bytes().strip()
        # The file already stores a valid Fernet key (url-safe b64)
        return raw

    # First run — generate a brand-new random key
    new_key: bytes = Fernet.generate_key()
    _KEY_FILE.write_bytes(new_key)

    # Restrict file permissions (owner read/write only)
    try:
        _KEY_FILE.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 0o600
    except OSError:
        # Windows may not support POSIX permissions — best effort
        pass

    return new_key


def save_settings(data: dict, path: Path) -> None:
    """Encrypt and write a settings dict to *path*."""
    f = Fernet(get_or_create_app_key())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(f.encrypt(json.dumps(data).encode("utf-8")))


def load_settings(path: Path) -> dict:
    """Read and decrypt a settings dict from *path*.

    Returns an empty dict if the file is missing or decryption fails.
    """
    if not path.exists():
        return {}
    try:
        f = Fernet(get_or_create_app_key())
        return json.loads(f.decrypt(path.read_bytes()))
    except Exception:
        return {}
