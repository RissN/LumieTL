"""Management, download, integrity check, and discovery of required ONNX models."""

import hashlib
from pathlib import Path
from typing import Callable
import httpx
from core.config import MODEL_DIR
from core.exceptions import ModelIntegrityError, ModelNotFoundError

# Standard models required by manga-image-translator pipeline
MODEL_REGISTRY: dict[str, dict] = {
    "detector": {
        "filename": "detector.onnx",
        "url": "https://github.com/zyddnys/manga-image-translator/releases/download/beta-0.3/comictextdetector.pt.onnx",
        "sha256": "4b5c7772c7205fcbeec8095d6ff17849cb151da1810c9c43d9b0572e903bc39c",
        "size_mb": 52,
        "description": "Deteksi area dan orientasi balon teks",
    },
    "ocr_48px": {
        "filename": "ocr_48px.onnx",
        "url": "https://github.com/zyddnys/manga-image-translator/releases/download/beta-0.3/ocr_48px.onnx",
        "sha256": "18fbaeb7cf5dd063162788e040fec7d812d33ff73e659b867c293ae793b8aa6f",
        "size_mb": 60,
        "description": "Optical Character Recognition (OCR) 48px",
    },
    "inpainter_lama": {
        "filename": "inpainter_lama.onnx",
        "url": "https://github.com/zyddnys/manga-image-translator/releases/download/beta-0.3/inpainting_lama_mpe.onnx",
        "sha256": "7a35fe634f19b16eaebf5e9545f4fa6e890c2a52dfbebeaa813e3bc256e300ce",
        "size_mb": 198,
        "description": "Inpainter pembersih balon teks (LaMa MPE)",
    },
}


def verify_model_integrity(path: Path, expected_sha256: str) -> bool:
    """Verify that file checksum matches the expected SHA-256 hash."""
    if not path.exists():
        return False
    if not expected_sha256 or expected_sha256.startswith("FILL_"):
        # For dev/flexible fallback if hash is unpinned
        return True

    hasher = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest().lower() == expected_sha256.lower()
    except Exception:
        return False


def get_model_status(target_dir: Path | None = None) -> list[dict]:
    """Retrieve detailed download and integrity status of all registered models."""
    base = target_dir or MODEL_DIR
    status_list = []
    for key, spec in MODEL_REGISTRY.items():
        file_path = base / spec["filename"]
        exists = file_path.exists()
        is_valid = verify_model_integrity(file_path, spec["sha256"]) if exists else False
        status_list.append(
            {
                "key": key,
                "name": spec["filename"],
                "description": spec["description"],
                "size_mb": spec["size_mb"],
                "downloaded": exists,
                "valid": is_valid,
                "path": str(file_path),
            }
        )
    return status_list


def models_ready(target_dir: Path | None = None) -> bool:
    """Check whether all required models are present and valid."""
    status = get_model_status(target_dir)
    return all(m["downloaded"] and m["valid"] for m in status)


def get_missing_models(target_dir: Path | None = None) -> list[dict]:
    """Return a list of models that still need to be downloaded or repaired."""
    status = get_model_status(target_dir)
    return [m for m in status if not (m["downloaded"] and m["valid"])]


async def download_model(
    model_key: str,
    target_dir: Path | None = None,
    progress_callback: Callable[[int, int, str], None] | None = None,
    cancel_check: Callable[[], bool] | None = None,
) -> Path:
    """
    Download an individual model asynchronously with progress reporting
    and atomic file replacement to prevent corrupted partially-written files.
    """
    if model_key not in MODEL_REGISTRY:
        raise ModelNotFoundError(f"Unknown model key: {model_key}")

    spec = MODEL_REGISTRY[model_key]
    dest_dir = target_dir or MODEL_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_file = dest_dir / spec["filename"]
    temp_file = dest_dir / f"{spec['filename']}.part"

    if dest_file.exists() and verify_model_integrity(dest_file, spec["sha256"]):
        if progress_callback:
            progress_callback(100, 100, f"{spec['filename']} sudah terverifikasi")
        return dest_file

    url = spec["url"]
    expected_size = spec["size_mb"] * 1024 * 1024

    try:
        async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                total_bytes = int(response.headers.get("content-length", expected_size))
                downloaded_bytes = 0

                with open(temp_file, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=65536):
                        if cancel_check and cancel_check():
                            temp_file.unlink(missing_ok=True)
                            raise ModelNotFoundError("Download dibatalkan oleh pengguna")

                        f.write(chunk)
                        downloaded_bytes += len(chunk)
                        if progress_callback and total_bytes > 0:
                            percent = int((downloaded_bytes / total_bytes) * 100)
                            msg = f"Mengunduh {spec['filename']} ({downloaded_bytes // (1024*1024)}MB / {total_bytes // (1024*1024)}MB)"
                            progress_callback(percent, 100, msg)

        # Verify integrity before finalizing
        if not verify_model_integrity(temp_file, spec["sha256"]):
            temp_file.unlink(missing_ok=True)
            raise ModelIntegrityError(
                f"Checksum SHA-256 model {spec['filename']} tidak cocok setelah diunduh"
            )

        # Atomic rename
        temp_file.replace(dest_file)
        return dest_file

    except Exception as e:
        temp_file.unlink(missing_ok=True)
        if isinstance(e, (ModelIntegrityError, ModelNotFoundError)):
            raise
        raise ModelNotFoundError(f"Gagal mengunduh model {spec['filename']}: {e}") from e
