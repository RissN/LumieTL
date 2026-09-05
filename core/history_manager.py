"""SQLite-based translation history manager."""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class HistoryEntry:
    id: Optional[int] = None
    timestamp: str = ""
    input_path: str = ""
    output_path: Optional[str] = None
    source_lang: str = "auto"
    target_lang: str = "ID"
    engine: str = "google"
    duration: float = 0.0
    success: bool = True
    error: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class HistoryManager:
    """Manages translation history records using SQLite."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS history (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp    TEXT NOT NULL,
                    input_path   TEXT NOT NULL,
                    output_path  TEXT,
                    source_lang  TEXT,
                    target_lang  TEXT,
                    engine       TEXT,
                    duration     REAL,
                    success      INTEGER NOT NULL DEFAULT 0,
                    error        TEXT DEFAULT ''
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_history_timestamp ON history(timestamp DESC)"
            )

    def add(self, entry: HistoryEntry) -> int:
        """Insert a new history entry and return its assigned ID."""
        with self._get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO history (
                    timestamp, input_path, output_path,
                    source_lang, target_lang, engine, duration, success, error
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.timestamp,
                    entry.input_path,
                    entry.output_path,
                    entry.source_lang,
                    entry.target_lang,
                    entry.engine,
                    entry.duration,
                    int(entry.success),
                    entry.error or "",
                ),
            )
            entry_id = cur.lastrowid
            entry.id = entry_id
            return entry_id

    def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        engine: str | None = None,
        success: bool | None = None,
    ) -> list[HistoryEntry]:
        """Fetch historical records with pagination and optional filtering."""
        query = "SELECT * FROM history WHERE 1=1"
        params: list = []

        if engine:
            query += " AND engine = ?"
            params.append(engine)

        if success is not None:
            query += " AND success = ?"
            params.append(1 if success else 0)

        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()

        return [
            HistoryEntry(
                id=row["id"],
                timestamp=row["timestamp"],
                input_path=row["input_path"],
                output_path=row["output_path"],
                source_lang=row["source_lang"],
                target_lang=row["target_lang"],
                engine=row["engine"],
                duration=float(row["duration"]),
                success=bool(row["success"]),
                error=row["error"] or "",
            )
            for row in rows
        ]

    def count(self, engine: str | None = None, success: bool | None = None) -> int:
        """Count total records matching filters."""
        query = "SELECT COUNT(*) as total FROM history WHERE 1=1"
        params: list = []
        if engine:
            query += " AND engine = ?"
            params.append(engine)
        if success is not None:
            query += " AND success = ?"
            params.append(1 if success else 0)

        with self._get_connection() as conn:
            row = conn.execute(query, params).fetchone()
            return row["total"] if row else 0

    def delete(self, entry_id: int) -> None:
        """Delete an individual entry by ID."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM history WHERE id = ?", (entry_id,))

    def clear_all(self) -> None:
        """Clear all historical records."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM history")
