"""API endpoints for reading and updating application settings and API keys."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from core.config import OUTPUT_DIR, SETTINGS_FILE
from security.keystore import get_keystore
from security.settings_crypto import load_settings, save_settings
from web.backend.middleware.auth import verify_auth

router = APIRouter(dependencies=[Depends(verify_auth)])
keystore = get_keystore()


class SettingsPayload(BaseModel):
    default_source_lang: str = "auto"
    default_target_lang: str = "ID"
    default_engine: str = "google"
    font_size: int = Field(14, ge=8, le=48)
    output_dir: str = str(OUTPUT_DIR)
    gpu_enabled: bool = False


class ApiKeyPayload(BaseModel):
    provider: str
    key: str


@router.get("")
async def get_app_settings():
    """Retrieve current application preferences."""
    saved = load_settings(SETTINGS_FILE)
    return {
        "default_source_lang": saved.get("default_source_lang", "auto"),
        "default_target_lang": saved.get("default_target_lang", "ID"),
        "default_engine": saved.get("default_engine", "google"),
        "font_size": saved.get("font_size", 14),
        "output_dir": saved.get("output_dir", str(OUTPUT_DIR)),
        "gpu_enabled": saved.get("gpu_enabled", False),
    }


@router.put("")
async def update_app_settings(payload: SettingsPayload):
    """Save application preferences encrypted to disk."""
    data = payload.model_dump()
    save_settings(data, SETTINGS_FILE)
    return {"updated": True, "settings": data}


@router.get("/api-keys")
async def get_api_keys_status():
    """Check whether third-party API keys are set, without exposing secret key contents."""
    return {
        "deepl_set": bool(keystore.get("deepl")),
        "openai_set": bool(keystore.get("openai")),
    }


@router.put("/api-keys")
async def set_api_key(payload: ApiKeyPayload):
    """Store an encrypted API key for DeepL or OpenAI."""
    prov = payload.provider.lower()
    if prov not in ("deepl", "openai"):
        raise HTTPException(status_code=400, detail="Provider tidak didukung (gunakan 'deepl' atau 'openai').")

    if payload.key.strip():
        keystore.save(prov, payload.key.strip())
    else:
        keystore.delete(prov)

    return {"status": "saved", "provider": prov}


@router.delete("/api-keys/{provider}")
async def remove_api_key(provider: str):
    """Remove a stored API key."""
    prov = provider.lower()
    keystore.delete(prov)
    return {"status": "deleted", "provider": prov}
