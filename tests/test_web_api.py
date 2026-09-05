"""Unit tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from web.backend.main import app

client = TestClient(app)


def test_api_status_index():
    response = client.get("/api/models/status")
    assert response.status_code == 200
    data = response.json()
    assert "ready" in data
    assert "models" in data
    assert len(data["models"]) >= 3


def test_api_settings_get_and_put():
    # GET settings
    get_res = client.get("/api/settings")
    assert get_res.status_code == 200
    current_settings = get_res.json()
    assert "default_source_lang" in current_settings
    assert "default_target_lang" in current_settings

    # PUT settings
    new_settings = {
        "default_source_lang": "KOR",
        "default_target_lang": "EN",
        "default_engine": "deepl",
        "font_size": 16,
        "output_dir": current_settings["output_dir"],
        "gpu_enabled": False,
    }
    put_res = client.put("/api/settings", json=new_settings)
    assert put_res.status_code == 200
    assert put_res.json()["updated"] is True

    # Check that settings updated
    check_res = client.get("/api/settings")
    assert check_res.json()["default_source_lang"] == "KOR"
    assert check_res.json()["font_size"] == 16


def test_api_keys_status_endpoint():
    res = client.get("/api/settings/api-keys")
    assert res.status_code == 200
    data = res.json()
    assert "deepl_set" in data
    assert "openai_set" in data
    # Ensure plaintext keys are never leaked in response
    assert "key" not in str(data)


def test_api_history_endpoints():
    res = client.get("/api/history")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data
