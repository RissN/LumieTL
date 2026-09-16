"""Encrypted keystore for third-party API keys.

Keys are stored in a single Fernet-encrypted JSON file. The actual
key values are never exposed through API responses — only boolean
flags indicating whether a key has been set.
"""

import json
from pathlib import Path

from cryptography.fernet import Fernet

from security.settings_crypto import get_or_create_app_key


class Keystore:
    """Read/write API keys to an encrypted file on disk."""

    def __init__(self, path: Path) -> None:
        self.path = path

    # -- internal helpers ---------------------------------------------------

    def _fernet(self) -> Fernet:
        return Fernet(get_or_create_app_key())

    def _load(self) -> dict[str, str]:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self._fernet().decrypt(self.path.read_bytes()))
        except Exception:
            return {}

    def _save(self, data: dict[str, str]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(
            self._fernet().encrypt(json.dumps(data).encode("utf-8"))
        )

    # -- public API ---------------------------------------------------------

    def save(self, provider: str, key: str) -> None:
        """Store an API key for *provider*."""
        data = self._load()
        data[provider] = key
        self._save(data)

    def get(self, provider: str) -> str | None:
        """Return the stored key for *provider*, or ``None``."""
        return self._load().get(provider)

    def delete(self, provider: str) -> None:
        """Remove the API key for *provider*."""
        data = self._load()
        data.pop(provider, None)
        self._save(data)

    def is_set(self, provider: str) -> bool:
        """Check whether a key exists for *provider* (without revealing it)."""
        return self.get(provider) is not None
