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
MODEL_REGISTRY: dict[str, dict] = {
    "comic-text-detector": {
        "url": "https://github.com/zyddnys/manga-image-translator/releases/download/beta-0.3/comictextdetector.pt",
        "sha256": "FILL_WITH_OFFICIAL_HASH",
        "size_mb": 52,
        "filename": "comictextdetector.pt",
    },
    "ocr_48px": {
        "url": "https://github.com/zyddnys/manga-image-translator/releases/download/beta-0.3/ocr-ctc.ckpt",
        "sha256": "FILL_WITH_OFFICIAL_HASH",
        "size_mb": 60,
        "filename": "ocr-ctc.ckpt",
    },
    "inpainter_lama": {
        "url": "https://github.com/zyddnys/manga-image-translator/releases/download/beta-0.3/inpainting_lama_mpe.ckpt",
        "sha256": "FILL_WITH_OFFICIAL_HASH",
        "size_mb": 198,
        "filename": "inpainting_lama_mpe.ckpt",
    },
}

ProgressCallback = Callable[[str, int, int], None]
"""Signature: (model_name, bytes_downloaded, bytes_total)"""


def get_model_status() -> list[dict]:
    """Return status information for every registered model."""
    statuses = []
    for name, info in MODEL_REGISTRY.items():
        dest = MODEL_DIR / info["filename"]
        downloaded = dest.exists()
        sha256_ok = False
        if downloaded and info["sha256"] != "FILL_WITH_OFFICIAL_HASH":
            sha256_ok = verify_integrity(dest, info["sha256"])
        statuses.append(
            {
                "name": name,
                "filename": info["filename"],
                "size_mb": info["size_mb"],
                "downloaded": downloaded,
                "sha256_ok": sha256_ok,
            }
        )
    return statuses


def models_ready() -> bool:
    """Return ``True`` if every required model is present (and valid)."""
    for name, info in MODEL_REGISTRY.items():
        path = MODEL_DIR / info["filename"]
        if not path.exists():
            return False
        # Skip integrity check when hash is a placeholder
        if info["sha256"] != "FILL_WITH_OFFICIAL_HASH":
            if not verify_integrity(path, info["sha256"]):
                return False
    return True


def verify_integrity(path: Path, expected: str) -> bool:
    """Verify a file's SHA256 hash against *expected*."""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest() == expected


async def download_all(progress_cb: ProgressCallback | None = None) -> None:
    """Download every model in the registry that is missing or invalid."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    for name, info in MODEL_REGISTRY.items():
        dest = MODEL_DIR / info["filename"]

        # Skip if already downloaded and valid
        if dest.exists():
            if info["sha256"] == "FILL_WITH_OFFICIAL_HASH":
                continue
            if verify_integrity(dest, info["sha256"]):
                continue

        audit("model_download_start", f"model={name}")
        await _download_file(info["url"], dest, name, progress_cb)

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
) -> None:
    """Stream-download a file with progress reporting."""
    async with httpx.AsyncClient(
        follow_redirects=True, timeout=httpx.Timeout(300.0)
    ) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            total = int(response.headers.get("content-length", 0))
            downloaded = 0
            with open(dest, "wb") as f:
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_cb:
                        progress_cb(name, downloaded, total)
