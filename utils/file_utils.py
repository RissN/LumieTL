"""File security, path sanitation, and image format validation utilities."""

import re
from pathlib import Path
from PIL import Image
from core.config import (
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE_BYTES,
    MAX_IMAGE_DIMENSION,
    MAX_IMAGE_PIXELS,
)
from core.exceptions import FileValidationError, SecurityError


def check_magic_bytes(path: Path) -> bool:
    """
    Validate actual file format using magic bytes signature.
    Supports JPEG, PNG, WebP (RIFF....WEBP), and AVIF (ftypavif/avis).
    """
    try:
        with open(path, "rb") as f:
            header = f.read(32)
    except Exception:
        return False

    if len(header) < 12:
        return False

    # JPEG signature
    if header.startswith(b"\xff\xd8\xff"):
        return True

    # PNG signature
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return True

    # WebP signature (RIFF + 4 bytes file length + WEBP)
    if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        return True

    # AVIF signature (ISO Base Media File Format: [4:8] == 'ftyp', [8:12] in ('avif', 'avis'))
    if header[4:8] == b"ftyp" and header[8:12] in (b"avif", b"avis", b"mif1"):
        return True

    return False


def validate_image_dimensions(path: Path) -> tuple[bool, str]:
    """
    Inspect image header to detect decompression bombs (pixel flood attacks).
    Does not decode the full raster bitmap into RAM.
    """
    try:
        with Image.open(path) as img:
            width, height = img.size
            total_pixels = width * height

            if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
                return (
                    False,
                    f"Image dimension ({width}x{height}) exceeds maximum allowed ({MAX_IMAGE_DIMENSION}px)",
                )

            if total_pixels > MAX_IMAGE_PIXELS:
                return (
                    False,
                    f"Total image pixels ({total_pixels}) exceeds safety limit ({MAX_IMAGE_PIXELS} pixels)",
                )

        return True, ""
    except Exception as e:
        return False, f"Could not inspect image metadata: {e}"


def validate_image_file(path: Path) -> tuple[bool, str]:
    """
    Comprehensive validation of an image file before processing.
    Checks: existence, file type, allowed extension, file size, magic bytes, and dimensions.
    """
    if not path.exists():
        return False, "File not found"

    if not path.is_file():
        return False, "Path is not a regular file"

    ext = path.suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Extension '{ext}' is not permitted"

    try:
        size = path.stat().st_size
    except Exception as e:
        return False, f"Cannot access file stat: {e}"

    if size == 0:
        return False, "File is empty (0 bytes)"

    if size > MAX_FILE_SIZE_BYTES:
        max_mb = MAX_FILE_SIZE_BYTES // (1024 * 1024)
        return False, f"File size ({size} bytes) exceeds limit ({max_mb} MB)"

    if not check_magic_bytes(path):
        return False, "Invalid image file header (magic bytes signature mismatch)"

    # Protect against decompression bombs
    dim_ok, dim_err = validate_image_dimensions(path)
    if not dim_ok:
        return False, dim_err

    return True, ""


def sanitize_filename(name: str) -> str:
    """Strip dangerous characters and path separators from filenames."""
    # Strip path separators and control characters
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    # Prevent directory traversal dots
    cleaned = re.sub(r"\.{2,}", "_", cleaned)
    cleaned = cleaned.strip(". _")
    # Ensure reasonable length
    return cleaned[:200] if cleaned else "output"


def safe_output_path(base_dir: Path, filename: str) -> Path:
    """
    Ensure the resolved destination stays strictly within base_dir.
    Guards against path traversal and prefix collision vulnerabilities.
    """
    resolved_base = base_dir.resolve()
    safe_name = sanitize_filename(filename)
    resolved_output = (resolved_base / safe_name).resolve()

    if not resolved_output.is_relative_to(resolved_base):
        raise SecurityError(f"Path traversal detected: {filename}")

    return resolved_output
