"""API endpoints for ONNX model status, discovery, and downloading."""

import asyncio
import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from core.config import MODEL_DIR
from core.model_manager import download_model, get_missing_models, get_model_status, models_ready
from backend.middleware.auth import verify_auth

router = APIRouter(dependencies=[Depends(verify_auth)])
MODEL_DOWNLOAD_TASKS: dict[str, dict[str, Any]] = {}


@router.get("/status")
async def get_models_status():
    """Check readiness and presence of all required ONNX models."""
    return {
        "ready": models_ready(),
        "models": get_model_status(),
    }


@router.post("/download")
async def start_models_download():
    """Trigger background download of any missing ONNX models."""
    missing = get_missing_models()
    if not missing:
        return {"status": "already_ready", "message": "Semua model sudah lengkap."}

    task_id = str(uuid.uuid4())
    MODEL_DOWNLOAD_TASKS[task_id] = {
        "status": "downloading",
        "progress": 0,
        "total": len(missing),
        "current_model": missing[0]["name"],
        "error": None,
    }

    asyncio.create_task(_download_worker(task_id, [m["key"] for m in missing]))
    return {"task_id": task_id, "total": len(missing)}


async def _download_worker(task_id: str, keys: list[str]):
    task = MODEL_DOWNLOAD_TASKS[task_id]
    for idx, key in enumerate(keys):
        task["current_model"] = key
        task["progress"] = int((idx / len(keys)) * 100)
        try:
            await download_model(key, MODEL_DIR)
        except Exception as e:
            task["status"] = "error"
            task["error"] = str(e)
            return

    task["progress"] = 100
    task["status"] = "finished"


@router.get("/download/{task_id}")
async def get_download_task_status(task_id: str):
    """Poll progress of a model download task."""
    if task_id not in MODEL_DOWNLOAD_TASKS:
        raise HTTPException(status_code=404, detail="Task unduhan model tidak ditemukan.")
    return MODEL_DOWNLOAD_TASKS[task_id]
