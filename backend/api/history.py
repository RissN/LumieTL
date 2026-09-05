"""API endpoints for managing translation history."""

from fastapi import APIRouter, Depends, HTTPException, Query
from core.config import HISTORY_DB
from core.history_manager import HistoryManager
from backend.middleware.auth import verify_auth

router = APIRouter(dependencies=[Depends(verify_auth)])
history_manager = HistoryManager(HISTORY_DB)


@router.get("")
async def get_history(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    engine: str | None = None,
    success: bool | None = None,
):
    """Retrieve paginated list of historical translations."""
    items = history_manager.get_all(limit=limit, offset=offset, engine=engine, success=success)
    total = history_manager.count(engine=engine, success=success)
    return {
        "items": [
            {
                "id": i.id,
                "timestamp": i.timestamp,
                "input_path": i.input_path,
                "output_path": i.output_path,
                "source_lang": i.source_lang,
                "target_lang": i.target_lang,
                "engine": i.engine,
                "duration": i.duration,
                "success": i.success,
                "error": i.error,
            }
            for i in items
        ],
        "total": total,
    }


@router.delete("/all")
async def clear_all_history():
    """Clear all records from translation history."""
    history_manager.clear_all()
    return {"cleared": True}


@router.delete("/{entry_id}")
async def delete_history_entry(entry_id: int):
    """Delete a single history entry by ID."""
    history_manager.delete(entry_id)
    return {"deleted": True}
