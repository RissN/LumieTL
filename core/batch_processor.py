"""Batch processing queue and task management.

Each batch is a *task* identified by a UUID. Files are processed
sequentially within a task (respecting the global semaphore), and
processing continues even if individual files fail.
"""

import asyncio
import io
import time
import uuid
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from core.config import OUTPUT_DIR, KEYS_FILE
from core.history_manager import HistoryEntry, HistoryManager
from core.translator import translate_image
from security.keystore import Keystore
from utils.file_utils import safe_output_path
from utils.logger import audit


class FileStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class BatchFile:
    """Status tracker for a single file within a batch."""

    filename: str
    status: FileStatus = FileStatus.PENDING
    duration: float = 0.0
    error: str = ""
    output_path: str | None = None


@dataclass
class BatchTask:
    """A complete batch translation task."""

    task_id: str
    source_lang: str
    target_lang: str
    engine: str
    files: list[BatchFile] = field(default_factory=list)
    cancelled: bool = False
    created_at: str = ""

    @property
    def total(self) -> int:
        return len(self.files)

    @property
    def done_count(self) -> int:
        return sum(
            1 for f in self.files if f.status in (FileStatus.DONE, FileStatus.ERROR)
        )

    @property
    def success_count(self) -> int:
        return sum(1 for f in self.files if f.status == FileStatus.DONE)

    @property
    def error_count(self) -> int:
        return sum(1 for f in self.files if f.status == FileStatus.ERROR)

    @property
    def is_complete(self) -> bool:
        return all(
            f.status in (FileStatus.DONE, FileStatus.ERROR, FileStatus.CANCELLED)
            for f in self.files
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "source_lang": self.source_lang,
            "target_lang": self.target_lang,
            "engine": self.engine,
            "cancelled": self.cancelled,
            "created_at": self.created_at,
            "total": self.total,
            "done": self.done_count,
            "success": self.success_count,
            "errors": self.error_count,
            "is_complete": self.is_complete,
            "files": [
                {
                    "filename": f.filename,
                    "status": f.status.value,
                    "duration": f.duration,
                    "error": f.error,
                    "output_path": f.output_path,
                }
                for f in self.files
            ],
        }


class BatchProcessor:
    """Manages batch translation tasks."""

    def __init__(
        self,
        semaphore: asyncio.Semaphore,
        history: HistoryManager,
        keystore: Keystore,
    ) -> None:
        self._semaphore = semaphore
        self._history = history
        self._keystore = keystore
        self._tasks: dict[str, BatchTask] = {}

    def create_task(
        self,
        filenames: list[str],
        source_lang: str,
        target_lang: str,
        engine: str,
    ) -> str:
        """Create a new batch task and return its ID."""
        task_id = uuid.uuid4().hex[:12]
        task = BatchTask(
            task_id=task_id,
            source_lang=source_lang,
            target_lang=target_lang,
            engine=engine,
            files=[BatchFile(filename=fn) for fn in filenames],
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._tasks[task_id] = task
        audit("batch_start", f"task={task_id} files={len(filenames)}")
        return task_id

    def get_task(self, task_id: str) -> BatchTask | None:
        return self._tasks.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if not task:
            return False
        task.cancelled = True
        for f in task.files:
            if f.status == FileStatus.PENDING:
                f.status = FileStatus.CANCELLED
        audit("batch_cancel", f"task={task_id}")
        return True

    async def process_task(
        self,
        task_id: str,
        file_contents: dict[str, bytes],
    ) -> None:
        """Process all files in a batch task sequentially."""
        task = self._tasks.get(task_id)
        if not task:
            return

        task_output_dir = OUTPUT_DIR / f"batch_{task_id}"
        task_output_dir.mkdir(parents=True, exist_ok=True)

        api_key = self._keystore.get(task.engine)

        for batch_file in task.files:
            if task.cancelled:
                if batch_file.status == FileStatus.PENDING:
                    batch_file.status = FileStatus.CANCELLED
                continue

            batch_file.status = FileStatus.PROCESSING
            start_time = time.time()

            try:
                # Write input to temp file
                input_path = task_output_dir / f"input_{batch_file.filename}"
                input_path.write_bytes(file_contents[batch_file.filename])

                output_path = safe_output_path(
                    task_output_dir, f"translated_{batch_file.filename}"
                )

                async with self._semaphore:
                    await translate_image(
                        input_path=input_path,
                        source_lang=task.source_lang,
                        target_lang=task.target_lang,
                        engine=task.engine,
                        output_path=output_path,
                        api_key=api_key,
                        cancel_check=lambda: task.cancelled,
                    )

                elapsed = time.time() - start_time
                batch_file.status = FileStatus.DONE
                batch_file.duration = round(elapsed, 2)
                batch_file.output_path = str(output_path)

                # Record in history
                self._history.add(
                    HistoryEntry(
                        id=0,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        input_filename=batch_file.filename,
                        output_path=str(output_path),
                        source_lang=task.source_lang,
                        target_lang=task.target_lang,
                        engine=task.engine,
                        duration=batch_file.duration,
                        success=True,
                    )
                )

                # Clean up input file
                input_path.unlink(missing_ok=True)

            except Exception as e:
                elapsed = time.time() - start_time
                batch_file.status = FileStatus.ERROR
                batch_file.duration = round(elapsed, 2)
                batch_file.error = str(e)

                self._history.add(
                    HistoryEntry(
                        id=0,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        input_filename=batch_file.filename,
                        output_path=None,
                        source_lang=task.source_lang,
                        target_lang=task.target_lang,
                        engine=task.engine,
                        duration=batch_file.duration,
                        success=False,
                        error=str(e),
                    )
                )

        audit(
            "batch_done",
            f"task={task_id} success={task.success_count} "
            f"failed={task.error_count}",
        )

    def build_zip(self, task_id: str) -> bytes | None:
        """Create a ZIP archive of all successful outputs for a batch task."""
        task = self._tasks.get(task_id)
        if not task:
            return None

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for batch_file in task.files:
                if batch_file.status == FileStatus.DONE and batch_file.output_path:
                    out_path = Path(batch_file.output_path)
                    if out_path.exists():
                        zf.write(out_path, arcname=batch_file.filename)

        return buf.getvalue()

    def build_log(self, task_id: str) -> str:
        """Generate a plain-text log for a batch task."""
        task = self._tasks.get(task_id)
        if not task:
            return ""

        lines = [
            f"LumieTL Batch Log — {task.created_at}",
            f"Task ID : {task.task_id}",
            f"Source  : {task.source_lang}",
            f"Target  : {task.target_lang}",
            f"Engine  : {task.engine}",
            f"Total   : {task.total}",
            f"Success : {task.success_count}",
            f"Errors  : {task.error_count}",
            "",
            "--- Files ---",
        ]
        for f in task.files:
            status_icon = {
                FileStatus.DONE: "✅",
                FileStatus.ERROR: "❌",
                FileStatus.CANCELLED: "⏹",
                FileStatus.PENDING: "⏸",
                FileStatus.PROCESSING: "⏳",
            }.get(f.status, "?")
            line = f"{status_icon} {f.filename}  [{f.status.value}]  {f.duration}s"
            if f.error:
                line += f"  — {f.error}"
            lines.append(line)

        return "\n".join(lines)
