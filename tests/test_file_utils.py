"""Unit tests for utils/file_utils.py."""

import pytest
from pathlib import Path
from PIL import Image
from core.exceptions import SecurityError
from utils.file_utils import (
    check_magic_bytes,
    safe_output_path,
    sanitize_filename,
    validate_image_dimensions,
    validate_image_file,
)


def test_sanitize_filename():
    assert sanitize_filename("chapter:01/test?.png") == "chapter_01_test_.png"
    assert sanitize_filename("...secret..") == "secret"
    assert sanitize_filename("") == "output"
    assert len(sanitize_filename("a" * 300)) == 200


def test_safe_output_path(tmp_path):
    base_dir = tmp_path / "output"
    base_dir.mkdir()

    # Normal safe file
    safe = safe_output_path(base_dir, "clean_file.png")
    assert safe.parent == base_dir.resolve()

    # Path traversal attack attempt
    traversal = safe_output_path(base_dir, "../../etc/passwd.jpg")
    assert traversal.is_relative_to(base_dir.resolve())
    assert ".." not in traversal.name


def test_magic_bytes_detection(tmp_path):
    # Valid PNG
    png_file = tmp_path / "valid.png"
    img = Image.new("RGB", (100, 100), color="blue")
    img.save(png_file, format="PNG")
    assert check_magic_bytes(png_file) is True

    # Valid JPEG
    jpg_file = tmp_path / "valid.jpg"
    img.save(jpg_file, format="JPEG")
    assert check_magic_bytes(jpg_file) is True

    # Fake file disguised as PNG
    fake_png = tmp_path / "fake.png"
    fake_png.write_text("Not a real image file, just plain text")
    assert check_magic_bytes(fake_png) is False

    valid, reason = validate_image_file(fake_png)
    assert valid is False
    assert "magic bytes" in reason.lower()


def test_decompression_bomb_protection(tmp_path):
    # Test dimension limit check
    huge_file = tmp_path / "huge.png"
    # Create image with dummy metadata or oversized dimensions
    img = Image.new("RGB", (10000, 1000), color="white")
    img.save(huge_file, format="PNG")

    valid, reason = validate_image_dimensions(huge_file)
    assert valid is False
    assert "exceeds maximum allowed" in reason
