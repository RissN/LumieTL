"""Image manipulation, resizing, and thumbnail generation helpers."""

from pathlib import Path
from PIL import Image
import io


def create_thumbnail(
    input_path: Path,
    thumb_path: Path,
    max_size: tuple[int, int] = (256, 256),
    format: str = "WEBP",
) -> Path:
    """Create and save a high-quality thumbnail image."""
    thumb_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(input_path) as img:
        # Convert RGBA/LA or palette to RGB if saving as JPEG
        if format.upper() in ("JPG", "JPEG") and img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        img.save(thumb_path, format=format, quality=80)
    return thumb_path


def get_image_info(path: Path) -> dict:
    """Return image dimensions, format, and mode without decoding full bitmap."""
    with Image.open(path) as img:
        return {
            "width": img.width,
            "height": img.height,
            "format": img.format,
            "mode": img.mode,
            "file_size": path.stat().st_size,
        }


def image_to_base64(path: Path, max_dimension: int | None = None) -> str:
    """Convert an image to a base64-encoded string, optionally downscaling if too large."""
    import base64

    with Image.open(path) as img:
        if max_dimension and (img.width > max_dimension or img.height > max_dimension):
            img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            raw_bytes = buf.getvalue()
        else:
            raw_bytes = path.read_bytes()

    return base64.b64encode(raw_bytes).decode("ascii")
