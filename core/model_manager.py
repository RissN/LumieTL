"""ONNX model download, verification, and management.

Model URLs and SHA256 hashes are placeholders — replace with actual
values from the manga-image-translator release assets.
"""

import hashlib
from pathlib import Path
from typing import Callable

import httpx

from core.config import MODEL_DIR
from core.exceptions import ModelIntegrityError
from utils.logger import audit

# ---------------------------------------------------------------------------
# Registry of required models.
# TODO: Fill with actual URLs and SHA256 hashes from manga-image-translator.
# ---------------------------------------------------------------------------
# Registry of required models with verified release URLs and expected sizes.
# ---------------------------------------------------------------------------
MODEL_REGISTRY: dict[str, dict] = {
    "comic-text-detector": {
        "url": "https://github.com/zyddnys/manga-image-translator/releases/download/beta-0.3/comictextdetector.pt",
        "sha256": "FILL_WITH_OFFICIAL_HASH",
        "size_mb": 76,
        "expected_bytes": 79948869,
        "min_bytes": 75_000_000,
        "filename": "comictextdetector.pt",
    },
    "ocr_48px": {
        "url": "https://github.com/zyddnys/manga-image-translator/releases/download/beta-0.3/ocr_ar_48px.ckpt",
        "sha256": "FILL_WITH_OFFICIAL_HASH",
        "size_mb": 195,
        "expected_bytes": 204290192,
        "min_bytes": 190_000_000,
        "filename": "ocr_ar_48px.ckpt",
    },
    "inpainter_lama": {
        "url": "https://github.com/zyddnys/manga-image-translator/releases/download/beta-0.3/inpainting_lama_mpe.ckpt",
        "sha256": "FILL_WITH_OFFICIAL_HASH",
        "size_mb": 104,
        "expected_bytes": 108580583,
        "min_bytes": 100_000_000,
        "filename": "inpainting_lama_mpe.ckpt",
    },
}

ProgressCallback = Callable[[str, int, int], None]
"""Signature: (model_name, bytes_downloaded, bytes_total)"""


def is_valid_model_file(path: Path, info: dict) -> bool:
    """Check if file exists and passes minimum byte size and optional sha256."""
    if not path.exists():
        return False
    try:
        # Check size to ensure file is not a 0-byte or interrupted partial download
        if path.stat().st_size < info.get("min_bytes", 1_000_000):
            return False
    except OSError:
        return False

    if info["sha256"] != "FILL_WITH_OFFICIAL_HASH":
        return verify_integrity(path, info["sha256"])
    return True


def get_model_status() -> list[dict]:
    """Return status information for every registered model."""
    statuses = []
    for name, info in MODEL_REGISTRY.items():
        dest = MODEL_DIR / info["filename"]
        downloaded = is_valid_model_file(dest, info)
        sha256_ok = False
        if downloaded and info["sha256"] != "FILL_WITH_OFFICIAL_HASH":
            sha256_ok = verify_integrity(dest, info["sha256"])
        statuses.append(
            {
                "name": name,
                "filename": info["filename"],
                "size_mb": info["size_mb"],
                "url": info["url"],
                "downloaded": downloaded,
                "sha256_ok": sha256_ok,
            }
        )
    return statuses


def models_ready() -> bool:
    """Return ``True`` if every required model is present (and valid)."""
    for name, info in MODEL_REGISTRY.items():
        path = MODEL_DIR / info["filename"]
        if not is_valid_model_file(path, info):
            return False
    return True


def verify_integrity(path: Path, expected: str) -> bool:
    """Verify a file's SHA256 hash against *expected*."""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest() == expected


async def download_all(progress_cb: ProgressCallback | None = None) -> None:
    """Download every model in the registry that is missing or invalid."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    for name, info in MODEL_REGISTRY.items():
        dest = MODEL_DIR / info["filename"]

        # Skip if already downloaded and valid
        if is_valid_model_file(dest, info):
            continue

        audit("model_download_start", f"model={name}")
        await _download_file(info["url"], dest, name, progress_cb, info.get("expected_bytes", 0))

        # Verify integrity when hash is available
        if info["sha256"] != "FILL_WITH_OFFICIAL_HASH":
            if not verify_integrity(dest, info["sha256"]):
                dest.unlink(missing_ok=True)
                raise ModelIntegrityError(
                    f"Integrity check failed for {name}"
                )

        audit("model_downloaded", f"model={name} sha256=ok")


async def _download_file(
    url: str,
    dest: Path,
    name: str,
    progress_cb: ProgressCallback | None,
    expected_bytes: int = 0,
) -> None:
    """Stream-download a file to a .part file, then rename atomically."""
    temp_dest = dest.with_name(f"{dest.name}.part")
    
    # Custom timeout with generous connect and read allowances
    timeout = httpx.Timeout(connect=60.0, read=900.0, write=60.0, pool=60.0)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        async with httpx.AsyncClient(
            follow_redirects=True, timeout=timeout, headers=headers
        ) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                total = int(response.headers.get("content-length", 0)) or expected_bytes
                downloaded = 0
                
                with open(temp_dest, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=65536):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_cb:
                            progress_cb(name, downloaded, total)

        # Atomic rename once completely downloaded
        if temp_dest.exists():
            if dest.exists():
                dest.unlink()
            temp_dest.rename(dest)

    except Exception:
        # Clean up partial download
        if temp_dest.exists():
            try:
                temp_dest.unlink()
            except OSError:
                pass
        raise

