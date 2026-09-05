"""Abstract Keystore interface and factory."""

import sys
from abc import ABC, abstractmethod


class KeystoreBase(ABC):
    """Abstract interface for secure API key storage."""

    @abstractmethod
    def save(self, provider: str, key: str) -> None:
        """Store an API key for a given provider."""

    @abstractmethod
    def get(self, provider: str) -> str | None:
        """Retrieve the API key for a provider, or None if not set."""

    @abstractmethod
    def delete(self, provider: str) -> None:
        """Delete an API key for a provider."""


def get_keystore() -> KeystoreBase:
    """
    Factory to return the encrypted FileKeystore implementation for the web server.
    """
    from core.config import KEYS_FILE
    from security.keystore_file import FileKeystore

    return FileKeystore(KEYS_FILE)
