"""Encrypted file keystore implementation for Linux / Web / fallback."""

import json
from pathlib import Path
from cryptography.fernet import Fernet
from security.keystore import KeystoreBase
from security.settings_crypto import get_master_key


class FileKeystore(KeystoreBase):
    """Stores API keys in an encrypted JSON file using Fernet."""

    def __init__(self, path: Path):
        self.path = path

    def _get_fernet(self) -> Fernet:
        return Fernet(get_master_key())

    def _load(self) -> dict:
        if not self.path.exists():
            return {}
        try:
            decrypted = self._get_fernet().decrypt(self.path.read_bytes())
            return json.loads(decrypted.decode("utf-8"))
        except Exception:
            return {}

    def _save_all(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        encrypted = self._get_fernet().encrypt(json.dumps(data).encode("utf-8"))
        self.path.write_bytes(encrypted)

    def save(self, provider: str, key: str) -> None:
        data = self._load()
        data[provider] = key
        self._save_all(data)

    def get(self, provider: str) -> str | None:
        return self._load().get(provider)

    def delete(self, provider: str) -> None:
        data = self._load()
        if provider in data:
            data.pop(provider, None)
            self._save_all(data)
