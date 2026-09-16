"""Model status and download endpoints."""

import asyncio
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from core.model_manager import (
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
    """Return readiness and per-model download status."""
    return {
        "ready": models_ready(),
        "models": get_model_status(),
    }


@router.post("/download")
async def start_model_download() -> dict:
    """Trigger model download in the background."""
    task_id = uuid.uuid4().hex[:12]

    _download_tasks[task_id] = {
        "status": "downloading",
        "progress": 0,
        "total": 0,
        "current_model": "",
        "error": None,
    }

    def progress_cb(model_name: str, downloaded: int, total: int) -> None:
        _download_tasks[task_id].update(
            {
                "current_model": model_name,
                "progress": downloaded,
                "total": total,
            }
        )

    async def _run_download() -> None:
        try:
            await download_all(progress_cb=progress_cb)
            _download_tasks[task_id]["status"] = "done"
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
