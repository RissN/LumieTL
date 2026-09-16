"""SQLite-backed translation history manager."""

import sqlite3
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


@dataclass
class HistoryEntry:
    """A single translation history record."""

    id: int
    timestamp: str
    input_filename: str
    output_path: Optional[str]
    source_lang: str
    target_lang: str
    engine: str
    duration: float
    success: bool
    error: str = ""


class HistoryManager:
    """CRUD operations for translation history stored in SQLite."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS history (
                    id             INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp      TEXT    NOT NULL,
                    input_filename TEXT    NOT NULL,
                    output_path    TEXT,
                    source_lang    TEXT,
                    target_lang    TEXT,
                    engine         TEXT,
                    duration       REAL,
                    success        INTEGER NOT NULL DEFAULT 0,
                    error          TEXT    DEFAULT ''
                )
                """
            )

    def add(self, entry: HistoryEntry) -> int:
        """Insert a new history entry and return its row ID."""
        with self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO history
                    (timestamp, input_filename, output_path,
                     source_lang, target_lang, engine,
                     duration, success, error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.timestamp,
                    entry.input_filename,
                    entry.output_path,
                    entry.source_lang,
                    entry.target_lang,
                    entry.engine,
                    entry.duration,
                    int(entry.success),
                    entry.error,
                ),
            )
            return cur.lastrowid  # type: ignore[return-value]

    def get_all(
        self,
        limit: int = 50,
        offset: int = 0,
        engine: str | None = None,
        status: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> tuple[list[HistoryEntry], int]:
        """Return a paginated, optionally filtered list of history entries.

        Returns ``(entries, total_count)``.
        """
        where_clauses: list[str] = []
        params: list = []

        if engine:
            where_clauses.append("engine = ?")
            params.append(engine)
        if status == "success":
            where_clauses.append("success = 1")
        elif status == "error":
            where_clauses.append("success = 0")
        if date_from:
            where_clauses.append("timestamp >= ?")
            params.append(date_from)
        if date_to:
            where_clauses.append("timestamp <= ?")
            params.append(date_to)

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        with self._conn() as conn:
            # Total count (for pagination)
            total = conn.execute(
                f"SELECT COUNT(*) FROM history {where_sql}", params
            ).fetchone()[0]

            rows = conn.execute(
                f"SELECT * FROM history {where_sql} ORDER BY id DESC LIMIT ? OFFSET ?",
                [*params, limit, offset],
            ).fetchall()

        entries = [HistoryEntry(*row) for row in rows]
        return entries, total

    def delete(self, entry_id: int) -> bool:
        """Delete a single entry by ID. Returns ``True`` if a row was removed."""
        with self._conn() as conn:
            cur = conn.execute("DELETE FROM history WHERE id = ?", (entry_id,))
            return cur.rowcount > 0

    def clear_all(self) -> int:
        """Delete all history entries. Returns the number of rows removed."""
        with self._conn() as conn:
            cur = conn.execute("DELETE FROM history")
            return cur.rowcount

    def count(self) -> int:
        """Return the total number of history entries."""
        with self._conn() as conn:
            return conn.execute("SELECT COUNT(*) FROM history").fetchone()[0]
