"""Image manipulation utilities (resize, convert, thumbnail)."""

import io
from pathlib import Path

from PIL import Image


def resize_image(
    image: Image.Image,
    max_width: int = 2048,
    max_height: int = 2048,
) -> Image.Image:
    """Resize *image* so it fits within the given bounds, preserving aspect ratio.

    Returns the original image unchanged if it already fits.
    """
    w, h = image.size
    if w <= max_width and h <= max_height:
        return image
    ratio = min(max_width / w, max_height / h)
    new_size = (int(w * ratio), int(h * ratio))
    return image.resize(new_size, Image.LANCZOS)


def convert_to_png(data: bytes) -> bytes:
    """Convert any supported image bytes to PNG format."""
    img = Image.open(io.BytesIO(data))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def create_thumbnail(data: bytes, size: tuple[int, int] = (256, 256)) -> bytes:
    """Create a JPEG thumbnail from image bytes."""
    img = Image.open(io.BytesIO(data))
    img.thumbnail(size, Image.LANCZOS)
    buf = io.BytesIO()
    # Convert RGBA → RGB for JPEG
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGB")
    img.save(buf, format="JPEG", quality=80)
    return buf.getvalue()


def image_to_base64_png(image_path: Path) -> str:
    """Read an image file and return its base64-encoded PNG representation."""
    import base64

    img = Image.open(image_path)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")
