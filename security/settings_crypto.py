"""Cryptographic utilities for protecting local settings and sensitive data."""

import base64
import json
import os
import platform
import uuid
import hashlib
from pathlib import Path
from cryptography.fernet import Fernet
from core.config import APP_DATA_DIR


def _get_machine_fingerprint() -> str:
    """Generate a platform-consistent machine identifier fingerprint."""
    try:
        node = platform.node()
        mac = uuid.getnode()
        return f"{node}:{mac}"
    except Exception:
        return "lumietl-default-node"


def get_master_key() -> bytes:
    """
    Retrieve or generate a cryptographically secure 32-byte master key.
    
    Order of precedence:
    1. LUMIETL_SECRET_KEY environment variable if provided.
    2. Persistent protected master key file with machine salt in APP_DATA_DIR.
    """
    env_key = os.environ.get("LUMIETL_SECRET_KEY")
    if env_key:
        digest = hashlib.sha256(env_key.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest)

    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    key_file = APP_DATA_DIR / ".master.key"
    fingerprint = _get_machine_fingerprint().encode("utf-8")

    if key_file.exists():
        try:
            raw_data = key_file.read_bytes()
            if len(raw_data) >= 32:
                derived = hashlib.sha256(raw_data + fingerprint).digest()
                return base64.urlsafe_b64encode(derived)
        except Exception:
            pass

    # Generate a new cryptographically secure random key
    random_bytes = os.urandom(32)
    derived = hashlib.sha256(random_bytes + fingerprint).digest()

    try:
        # Write securely
        key_file.write_bytes(random_bytes)
        # Attempt to restrict file permissions on POSIX systems
        if os.name == "posix":
            os.chmod(key_file, 0o600)
    except Exception:
        pass

    return base64.urlsafe_b64encode(derived)


def save_settings(data: dict, path: Path) -> None:
    """Encrypt and save a settings dictionary to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fernet = Fernet(get_master_key())
    serialized = json.dumps(data, ensure_ascii=False).encode("utf-8")
    encrypted = fernet.encrypt(serialized)
    path.write_bytes(encrypted)


def load_settings(path: Path) -> dict:
    """Read and decrypt settings dictionary from disk, returning {} if missing or corrupted."""
    if not path.exists():
        return {}
    try:
        fernet = Fernet(get_master_key())
        decrypted = fernet.decrypt(path.read_bytes())
        return json.loads(decrypted.decode("utf-8"))
    except Exception:
        return {}
