"""Translation endpoints — single image and batch processing."""

import asyncio
import base64
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Form, HTTPException, UploadFile
from fastapi.responses import Response

from core.batch_processor import BatchProcessor
from core.config import (
    KEYS_FILE,
    MAX_CONCURRENT_TRANSLATIONS,
    MAX_FILE_SIZE_BYTES,
    MAX_FILE_SIZE_MB,
    OUTPUT_DIR,
)
from core.history_manager import HistoryEntry, HistoryManager
from core.translator import translate_image
from security.keystore import Keystore
from utils.file_utils import safe_output_path, validate_image_bytes
from utils.image_utils import image_to_base64_png
from utils.logger import audit

router = APIRouter()

# Global semaphore — at most 3 images translated concurrently
_semaphore = asyncio.Semaphore(MAX_CONCURRENT_TRANSLATIONS)

# These will be injected in main.py via the router's state
_history: HistoryManager | None = None
_keystore: Keystore | None = None
_batch: BatchProcessor | None = None


def init_translate_deps(
    history: HistoryManager,
    keystore: Keystore,
    batch: BatchProcessor,
) -> None:
    """Inject shared dependencies (called once from main.py)."""
    global _history, _keystore, _batch
    _history = history
    _keystore = keystore
    _batch = batch


async def _read_and_validate(file: UploadFile) -> bytes:
    """Read an upload and validate size + type."""
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE_MB}MB",
        )
    ok, msg = validate_image_bytes(content, file.filename or "unknown")
    if not ok:
        raise HTTPException(status_code=422, detail=msg)
    return content


# ── Single translation ────────────────────────────────────────────────

@router.post("/single")
async def translate_single(
    file: UploadFile,
    source_lang: str = Form("auto"),
    target_lang: str = Form("ID"),
    engine: str = Form("google"),
) -> dict:
    """Translate a single image and return the result as base64 PNG."""
    content = await _read_and_validate(file)
    filename = file.filename or "input.png"

    # Write input to temp file
    input_dir = OUTPUT_DIR / "single"
    input_dir.mkdir(parents=True, exist_ok=True)
    input_path = input_dir / f"input_{filename}"
    input_path.write_bytes(content)

    output_path = safe_output_path(input_dir, f"translated_{filename}")

    api_key = _keystore.get(engine) if _keystore else None

    start_time = time.time()
    try:
        async with _semaphore:
            await translate_image(
                input_path=input_path,
                source_lang=source_lang,
                target_lang=target_lang,
                engine=engine,
                output_path=output_path,
                api_key=api_key,
            )
        duration = round(time.time() - start_time, 2)

        result_b64 = image_to_base64_png(output_path)

        # Record in history
        if _history:
            _history.add(
                HistoryEntry(
                    id=0,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    input_filename=filename,
                    output_path=str(output_path),
                    source_lang=source_lang,
                    target_lang=target_lang,
                    engine=engine,
                    duration=duration,
                    success=True,
                )
            )

        audit("translate_done", f"duration={duration}s file={filename}")
        return {
            "result_image_base64": result_b64,
            "duration": duration,
        }

    except HTTPException:
        raise
    except Exception as e:
        duration = round(time.time() - start_time, 2)
        if _history:
            _history.add(
                HistoryEntry(
                    id=0,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    input_filename=filename,
                    output_path=None,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    engine=engine,
                    duration=duration,
                    success=False,
                    error=str(e),
                )
            )
        audit("translate_failed", f"error={e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up input temp file
        input_path.unlink(missing_ok=True)


# ── Batch translation ─────────────────────────────────────────────────

@router.post("/batch/start")
async def batch_start(
    files: list[UploadFile],
    source_lang: str = Form("auto"),
    target_lang: str = Form("ID"),
    engine: str = Form("google"),
) -> dict:
    """Start a batch translation job."""
    if not _batch:
        raise HTTPException(status_code=500, detail="Batch processor not initialized")

    if not files:
        raise HTTPException(status_code=422, detail="No files provided")

    # Read and validate all files first
    file_contents: dict[str, bytes] = {}
    filenames: list[str] = []

    for f in files:
        content = await _read_and_validate(f)
        fname = f.filename or f"file_{len(filenames)}.png"
        file_contents[fname] = content
        filenames.append(fname)

    task_id = _batch.create_task(filenames, source_lang, target_lang, engine)

    # Start processing in background
    asyncio.create_task(_batch.process_task(task_id, file_contents))

    return {"task_id": task_id}


@router.get("/batch/{task_id}")
async def batch_status(task_id: str) -> dict:
    """Get status of a batch task."""
    if not _batch:
        raise HTTPException(status_code=500, detail="Batch processor not initialized")

    task = _batch.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Batch task not found")

    return task.to_dict()


@router.delete("/batch/{task_id}")
async def batch_cancel(task_id: str) -> dict:
    """Cancel a running batch task."""
    if not _batch:
        raise HTTPException(status_code=500, detail="Batch processor not initialized")

    cancelled = _batch.cancel_task(task_id)
    if not cancelled:
        raise HTTPException(status_code=404, detail="Batch task not found")

    return {"cancelled": True}


@router.get("/batch/{task_id}/download")
async def batch_download(task_id: str) -> Response:
    """Download all successful results as a ZIP file."""
    if not _batch:
        raise HTTPException(status_code=500, detail="Batch processor not initialized")

    zip_bytes = _batch.build_zip(task_id)
    if zip_bytes is None:
        raise HTTPException(status_code=404, detail="Batch task not found")

    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="LumieTL_batch_{task_id}.zip"'
        },
    )


@router.get("/batch/{task_id}/log")
async def batch_log(task_id: str) -> Response:
    """Download batch processing log as a text file."""
    if not _batch:
        raise HTTPException(status_code=500, detail="Batch processor not initialized")

    log_text = _batch.build_log(task_id)
    if not log_text:
        raise HTTPException(status_code=404, detail="Batch task not found")

    return Response(
        content=log_text.encode("utf-8"),
        media_type="text/plain; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="LumieTL_batch_{task_id}.txt"'
        },
    )
