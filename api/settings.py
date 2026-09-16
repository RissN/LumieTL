"""Settings and API key management endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.config import (
    KEYS_FILE,
    SETTINGS_FILE,
    SOURCE_LANGS,
    TARGET_LANGS,
    TRANSLATOR_ENGINES,
)
from security.keystore import Keystore
from security.settings_crypto import load_settings, save_settings
from utils.logger import audit

router = APIRouter()

# Will be injected from main.py
_keystore: Keystore | None = None

# Default settings
_DEFAULTS: dict = {
    "default_source_lang": "auto",
    "default_target_lang": "ID",
    "default_engine": "google",
    "output_dir": "",
    "gpu_enabled": False,
}


def init_settings_deps(keystore: Keystore) -> None:
    """Inject the shared Keystore instance."""
    global _keystore
    _keystore = keystore


# ── Settings ──────────────────────────────────────────────────────────

@router.get("")
async def get_settings() -> dict:
    """Return current application settings."""
    saved = load_settings(SETTINGS_FILE)
    # Merge with defaults (saved values take priority)
    result = {**_DEFAULTS, **saved}
    # Also include available options for the frontend
    result["available_source_langs"] = SOURCE_LANGS
    result["available_target_langs"] = TARGET_LANGS
    result["available_engines"] = TRANSLATOR_ENGINES
    return result


class SettingsUpdate(BaseModel):
    default_source_lang: str | None = None
    default_target_lang: str | None = None
    default_engine: str | None = None
    output_dir: str | None = None
    gpu_enabled: bool | None = None


@router.put("")
async def update_settings(body: SettingsUpdate) -> dict:
    """Update application settings."""
    current = load_settings(SETTINGS_FILE)

    updates = body.model_dump(exclude_none=True)
    current.update(updates)

    save_settings(current, SETTINGS_FILE)
    audit("settings_updated", f"keys={list(updates.keys())}")

    return {"updated": True, "settings": current}


@router.post("/reset")
async def reset_settings() -> dict:
    """Reset settings to defaults."""
    save_settings(_DEFAULTS, SETTINGS_FILE)
    audit("settings_reset", "")
    return {"reset": True, "settings": _DEFAULTS}


# ── API Keys ──────────────────────────────────────────────────────────

@router.get("/api-keys")
async def get_api_key_status() -> dict:
    """Return whether each provider's API key is configured.

    NEVER returns the actual key value.
    """
    if not _keystore:
        raise HTTPException(status_code=500, detail="Keystore not initialized")

    return {
        "deepl_set": _keystore.is_set("deepl"),
        "openai_set": _keystore.is_set("openai"),
    }


class ApiKeyUpdate(BaseModel):
    provider: str
    key: str


@router.put("/api-keys")
async def save_api_key(body: ApiKeyUpdate) -> dict:
    """Store an encrypted API key for a provider."""
    if not _keystore:
        raise HTTPException(status_code=500, detail="Keystore not initialized")

    if body.provider not in ("deepl", "openai"):
        raise HTTPException(status_code=422, detail="Invalid provider")

    if not body.key.strip():
        raise HTTPException(status_code=422, detail="Key cannot be empty")

    _keystore.save(body.provider, body.key.strip())
    audit("api_key_saved", f"provider={body.provider}")

    return {"saved": True}


@router.delete("/api-keys/{provider}")
async def delete_api_key(provider: str) -> dict:
    """Remove the API key for a provider."""
    if not _keystore:
        raise HTTPException(status_code=500, detail="Keystore not initialized")

    if provider not in ("deepl", "openai"):
        raise HTTPException(status_code=422, detail="Invalid provider")

    _keystore.delete(provider)
    audit("api_key_deleted", f"provider={provider}")

    return {"deleted": True}
