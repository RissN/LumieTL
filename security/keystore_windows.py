"""Windows Credential Manager Keystore implementation."""

import keyring
from security.keystore import KeystoreBase

SERVICE_NAME = "LumieTL"


class WindowsKeystore(KeystoreBase):
    """Stores credentials securely in Windows Credential Manager."""

    def save(self, provider: str, key: str) -> None:
        keyring.set_password(SERVICE_NAME, provider, key)

    def get(self, provider: str) -> str | None:
        return keyring.get_password(SERVICE_NAME, provider)

    def delete(self, provider: str) -> None:
        try:
            keyring.delete_password(SERVICE_NAME, provider)
        except Exception:
            pass
