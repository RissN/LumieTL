"""Model status and download endpoints."""

import asyncio
import os
import subprocess
import sys
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from core.config import MODEL_DIR
from core.model_manager import (
    MODEL_REGISTRY,
    download_all,
    get_model_status,
    models_ready,
)
from utils.logger import audit

router = APIRouter()

# Track active download tasks
_download_tasks: dict[str, dict[str, Any]] = {}


@router.get("/status")
async def model_status() -> dict:
    """Return readiness, directory path, and per-model download status."""
    return {
        "ready": models_ready(),
        "model_dir": str(MODEL_DIR),
        "models": get_model_status(),
    }


@router.post("/open-folder")
async def open_models_folder() -> dict:
    """Open the models directory in the OS file explorer."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    try:
        if sys.platform == "win32":
            os.startfile(str(MODEL_DIR))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(MODEL_DIR)])
        else:
            subprocess.Popen(["xdg-open", str(MODEL_DIR)])
        return {"status": "ok", "path": str(MODEL_DIR)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to open folder: {e}")


@router.post("/download")
async def start_model_download() -> dict:
    """Trigger model download in the background with progress reporting."""
    task_id = uuid.uuid4().hex[:12]
    total_models = len(MODEL_REGISTRY)
    completed_models: list[str] = []

    _download_tasks[task_id] = {
        "status": "downloading",
        "progress": 0,
        "total": 0,
        "current_model": "",
        "completed_count": 0,
        "total_models": total_models,
        "completed_models": completed_models,
        "percent": 0,
        "error": None,
    }

    last_model = ""

    def progress_cb(model_name: str, downloaded: int, total: int) -> None:
        nonlocal last_model
        if last_model and last_model != model_name and last_model not in completed_models:
            completed_models.append(last_model)
        last_model = model_name

        pct = round((downloaded / total) * 100) if total > 0 else 0
        overall_pct = round(((len(completed_models) + (downloaded / total if total > 0 else 0)) / total_models) * 100)

        _download_tasks[task_id].update(
            {
                "current_model": model_name,
                "progress": downloaded,
                "total": total,
                "percent": pct,
                "overall_percent": overall_pct,
                "completed_count": len(completed_models),
            }
        )

    async def _run_download() -> None:
        try:
            await download_all(progress_cb=progress_cb)
            _download_tasks[task_id]["status"] = "done"
            _download_tasks[task_id]["percent"] = 100
            _download_tasks[task_id]["overall_percent"] = 100
            audit("model_download_complete", f"task={task_id}")
        except Exception as e:
            _download_tasks[task_id]["status"] = "error"
            _download_tasks[task_id]["error"] = str(e)
            audit("model_download_failed", f"task={task_id} error={e}")

    asyncio.create_task(_run_download())
    audit("model_download_start", f"task={task_id}")

    return {"task_id": task_id}


@router.get("/download/{task_id}")
async def download_progress(task_id: str) -> dict:
    """Poll model download progress."""
    task = _download_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Download task not found")
    return task

