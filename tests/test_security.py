"""Unit tests for security modules (settings encryption and keystore)."""

from pathlib import Path
from security.keystore_file import FileKeystore
from security.settings_crypto import load_settings, save_settings


def test_settings_encryption(tmp_path):
    settings_file = tmp_path / "settings.enc"
    original_data = {
        "default_source_lang": "JPN",
        "default_target_lang": "ID",
        "engine": "deepl",
        "font_size": 14,
    }

    save_settings(original_data, settings_file)
    assert settings_file.exists()
    # Ensure disk content is encrypted and not raw JSON
    raw_content = settings_file.read_bytes()
    assert b"default_source_lang" not in raw_content

    loaded_data = load_settings(settings_file)
    assert loaded_data == original_data


def test_file_keystore(tmp_path):
    keys_file = tmp_path / "keys.enc"
    keystore = FileKeystore(keys_file)

    # Save keys
    keystore.save("deepl", "test-deepl-key-12345")
    keystore.save("openai", "sk-proj-test987654321")

    # Read keys
    assert keystore.get("deepl") == "test-deepl-key-12345"
    assert keystore.get("openai") == "sk-proj-test987654321"
    assert keystore.get("unknown_provider") is None

    # Delete key
    keystore.delete("deepl")
    assert keystore.get("deepl") is None
    assert keystore.get("openai") == "sk-proj-test987654321"
