"""Translation history endpoints."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from core.config import HISTORY_DB
from core.history_manager import HistoryManager
from utils.logger import audit

router = APIRouter()

# Will be injected from main.py
_history: HistoryManager | None = None


def init_history_deps(history: HistoryManager) -> None:
    """Inject the shared HistoryManager instance."""
    global _history
    _history = history


@router.get("")
async def get_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    engine: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> dict:
    """Return paginated translation history with optional filters."""
    if not _history:
        raise HTTPException(status_code=500, detail="History not initialized")

    entries, total = _history.get_all(
        limit=limit,
        offset=offset,
        engine=engine,
        status=status,
        date_from=date_from,
        date_to=date_to,
    )

    return {
        "items": [
            {
                "id": e.id,
                "timestamp": e.timestamp,
                "input_filename": e.input_filename,
                "output_path": e.output_path,
                "source_lang": e.source_lang,
                "target_lang": e.target_lang,
                "engine": e.engine,
                "duration": e.duration,
                "success": e.success,
                "error": e.error,
            }
            for e in entries
        ],
        "total": total,
    }


@router.delete("/all")
async def clear_all_history() -> dict:
    """Delete all history entries."""
    if not _history:
        raise HTTPException(status_code=500, detail="History not initialized")

    count = _history.clear_all()
    audit("history_cleared", f"deleted={count}")
    return {"deleted": count}


@router.delete("/{entry_id}")
async def delete_history_entry(entry_id: int) -> dict:
    """Delete a single history entry."""
    if not _history:
        raise HTTPException(status_code=500, detail="History not initialized")

    deleted = _history.delete(entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="History entry not found")

    audit("history_deleted", f"id={entry_id}")
    return {"deleted": True}
