"""API endpoints for single and batch image translation."""

import asyncio
import uuid
from pathlib import Path
from typing import Any
import anyio
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from core.config import APP_DATA_DIR, HISTORY_DB, OUTPUT_DIR
from core.history_manager import HistoryEntry, HistoryManager
from core.translator import translate_image
from security.keystore import get_keystore
from utils.file_utils import safe_output_path, sanitize_filename, validate_image_file
from utils.image_utils import image_to_base64
from backend.middleware.auth import verify_auth

router = APIRouter(dependencies=[Depends(verify_auth)])
history_manager = HistoryManager(HISTORY_DB)
keystore = get_keystore()

# In-memory batch tasks tracker
BATCH_TASKS: dict[str, dict[str, Any]] = {}


@router.post("/single")
async def translate_single_image(
    file: UploadFile = File(...),
    source_lang: str = Form("auto"),
    target_lang: str = Form("ID"),
    engine: str = Form("google"),
):
    """Translate an uploaded image file."""
    temp_dir = APP_DATA_DIR / "temp_uploads"
    temp_dir.mkdir(parents=True, exist_ok=True)

    safe_name = sanitize_filename(file.filename or "upload.png")
    temp_input = temp_dir / f"upload_{uuid.uuid4().hex[:8]}_{safe_name}"

    try:
        content = await file.read()
        temp_input.write_bytes(content)

        # Validate security & format
        is_valid, err_msg = validate_image_file(temp_input)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"File tidak valid: {err_msg}")

        # Resolve API key if needed
        api_key = None
        if engine in ("deepl", "openai"):
            api_key = keystore.get(engine)
            if not api_key:
                raise HTTPException(
                    status_code=400,
                    detail=f"API Key untuk engine '{engine}' belum diatur pada pengaturan server.",
                )

        output_filename = f"web_{uuid.uuid4().hex[:8]}_{safe_name}"
        output_path = safe_output_path(OUTPUT_DIR, output_filename)

        # Execute translation pipeline without freezing the async event loop
        async def _exec():
            return await translate_image(
                input_path=temp_input,
                source_lang=source_lang,
                target_lang=target_lang,
                engine=engine,
                output_path=output_path,
                api_key=api_key,
            )

        out_path, duration = await _exec()

        # Generate base64 result for instant display
        b64_data = image_to_base64(out_path)

        # Save to history
        history_manager.add(
            HistoryEntry(
                input_path=str(temp_input),
                output_path=str(out_path),
                source_lang=source_lang,
                target_lang=target_lang,
                engine=engine,
                duration=duration,
                success=True,
            )
        )

        return {
            "result_image_base64": b64_data,
            "duration": round(duration, 2),
            "output_filename": output_filename,
        }

    except HTTPException:
        raise
    except Exception as e:
        history_manager.add(
            HistoryEntry(
                input_path=file.filename or "unknown",
                output_path=None,
                source_lang=source_lang,
                target_lang=target_lang,
                engine=engine,
                duration=0.0,
                success=False,
                error=str(e),
            )
        )
        raise HTTPException(status_code=500, detail=f"Proses translasi gagal: {e}")
    finally:
        # Clean up temporary upload
        temp_input.unlink(missing_ok=True)


@router.post("/batch/start")
async def start_batch_translation(
    files: list[UploadFile] = File(...),
    source_lang: str = Form("auto"),
    target_lang: str = Form("ID"),
    engine: str = Form("google"),
):
    """Start asynchronous batch translation of multiple uploaded files."""
    if not files:
        raise HTTPException(status_code=400, detail="Tidak ada berkas yang diunggah.")

    task_id = str(uuid.uuid4())
    temp_dir = APP_DATA_DIR / "batch_uploads" / task_id
    temp_dir.mkdir(parents=True, exist_ok=True)

    file_paths: list[Path] = []
    for f in files:
        safe_name = sanitize_filename(f.filename or "image.png")
        p = temp_dir / safe_name
        p.write_bytes(await f.read())
        file_paths.append(p)

    api_key = keystore.get(engine) if engine in ("deepl", "openai") else None

    BATCH_TASKS[task_id] = {
        "status": "processing",
        "progress": 0,
        "total": len(file_paths),
        "results": [],
        "cancelled": False,
    }

    # Run batch worker in background task
    asyncio.create_task(_run_background_batch(task_id, file_paths, source_lang, target_lang, engine, api_key))

    return {"task_id": task_id, "total": len(file_paths)}


async def _run_background_batch(
    task_id: str,
    file_paths: list[Path],
    source_lang: str,
    target_lang: str,
    engine: str,
    api_key: str | None,
):
    task = BATCH_TASKS[task_id]
    for idx, p in enumerate(file_paths):
        if task["cancelled"]:
            task["results"].append({"name": p.name, "status": "skipped", "error": "Cancelled"})
            continue

        out_name = f"batch_{task_id[:6]}_{p.name}"
        out_p = safe_output_path(OUTPUT_DIR, out_name)

        try:
            _, dur = await translate_image(
                input_path=p,
                source_lang=source_lang,
                target_lang=target_lang,
                engine=engine,
                output_path=out_p,
                api_key=api_key,
                cancel_check=lambda: task["cancelled"],
            )
            task["results"].append({"name": p.name, "status": "success", "duration": round(dur, 2)})
        except Exception as e:
            task["results"].append({"name": p.name, "status": "error", "error": str(e)})

        task["progress"] = idx + 1

    task["status"] = "finished" if not task["cancelled"] else "cancelled"


@router.get("/batch/{task_id}")
async def get_batch_status(task_id: str):
    """Retrieve progress status of a running or completed batch task."""
    if task_id not in BATCH_TASKS:
        raise HTTPException(status_code=404, detail="Task batch tidak ditemukan.")
    return BATCH_TASKS[task_id]


@router.delete("/batch/{task_id}")
async def cancel_batch_task(task_id: str):
    """Cancel an active batch task."""
    if task_id not in BATCH_TASKS:
        raise HTTPException(status_code=404, detail="Task batch tidak ditemukan.")
    BATCH_TASKS[task_id]["cancelled"] = True
    return {"cancelled": True}
