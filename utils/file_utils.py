"""File validation, sanitization, and path-traversal protection."""

import re
from pathlib import Path

from core.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB

# Magic byte signatures for supported image formats.
# AVIF uses the ISO BMFF container — bytes 4..11 are "ftypavif" (or mif1).
MAGIC_BYTES: dict[bytes, str] = {
    b"\xff\xd8\xff": "jpeg",
    b"\x89PNG\r\n\x1a\n": "png",
    b"RIFF": "webp",  # WebP is RIFF container; further bytes identify VP8
}


def _check_magic(data: bytes) -> bool:
    """Return ``True`` if *data* starts with a recognised image signature."""
    # Standard magic byte check
    for magic in MAGIC_BYTES:
        if data[: len(magic)] == magic:
            return True

    # AVIF — ISO BMFF: bytes 4..8 == "ftyp" and brand contains "avif" or "mif1"
    if len(data) >= 12 and data[4:8] == b"ftyp":
        brand = data[8:12]
        if brand in (b"avif", b"mif1", b"avis"):
            return True

    return False


def validate_image_bytes(data: bytes, filename: str) -> tuple[bool, str]:
    """Validate uploaded image bytes (extension + size + magic bytes).

    Returns ``(True, "")`` on success, or ``(False, reason)`` on failure.
    """
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Extension not allowed: {ext}"
    if len(data) > MAX_FILE_SIZE_BYTES:
        return False, f"File too large (max {MAX_FILE_SIZE_MB}MB)"
    if not _check_magic(data):
        return False, "Invalid image file (magic bytes mismatch)"
    return True, ""


def sanitize_filename(name: str) -> str:
    """Remove dangerous characters from a filename."""
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    name = name.strip(". ")
    return name[:200] if name else "output"


def safe_output_path(base_dir: Path, filename: str) -> Path:
    """Return a resolved path inside *base_dir*, preventing traversal.

    Raises ``ValueError`` if the result escapes *base_dir*.
    """
    safe_name = sanitize_filename(filename)
    output = (base_dir / safe_name).resolve()
    if not str(output).startswith(str(base_dir.resolve())):
        raise ValueError(f"Path traversal detected: {filename}")
    return output
