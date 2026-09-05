"""Batch translation processor with queue management, pause/resume, and auto-skip resilience."""

import asyncio
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional
from core.config import ALLOWED_EXTENSIONS
from core.history_manager import HistoryEntry, HistoryManager
from core.translator import translate_image
from utils.file_utils import safe_output_path
from utils.logger import get_logger

logger = get_logger()


@dataclass
class BatchItem:
    input_path: Path
    output_path: Path
    status: str = "pending"  # pending, processing, success, error, skipped
    duration: float = 0.0
    error: str = ""


class BatchProcessor:
    """Processes a batch queue of images with controls and progress reporting."""

    def __init__(
        self,
        input_dir: Path,
        output_dir: Optional[Path] = None,
        source_lang: str = "auto",
        target_lang: str = "ID",
        engine: str = "google",
        api_key: Optional[str] = None,
        model_dir: Optional[Path] = None,
        history_manager: Optional[HistoryManager] = None,
        extension_filter: Optional[set[str]] = None,
    ):
        self.input_dir = input_dir
        self.output_dir = output_dir or Path(f"{str(input_dir)}_translated")
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.engine = engine
        self.api_key = api_key
        self.model_dir = model_dir
        self.history_manager = history_manager
        self.extension_filter = extension_filter or ALLOWED_EXTENSIONS

        self.items: list[BatchItem] = []
        self._is_paused = False
        self._is_cancelled = False
        self._scan_files()

    def _scan_files(self) -> None:
        """Scan input directory for matching image files."""
        if not self.input_dir.exists() or not self.input_dir.is_dir():
            return

        for p in sorted(self.input_dir.iterdir()):
            if p.is_file() and p.suffix.lower() in self.extension_filter:
                safe_out = safe_output_path(self.output_dir, p.name)
                self.items.append(BatchItem(input_path=p, output_path=safe_out))

    def pause(self) -> None:
        self._is_paused = True

    def resume(self) -> None:
        self._is_paused = False

    def cancel(self) -> None:
        self._is_cancelled = True

    def is_paused(self) -> bool:
        return self._is_paused

    def is_cancelled(self) -> bool:
        return self._is_cancelled

    async def run(
        self,
        item_progress_callback: Optional[Callable[[int, int, BatchItem], None]] = None,
    ) -> list[BatchItem]:
        """
        Execute the batch queue.
        Guarantees that a failure in one file does not halt the entire queue.
        """
        total = len(self.items)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        for idx, item in enumerate(self.items):
            if self._is_cancelled:
                item.status = "skipped"
                item.error = "Cancelled by user"
                if item_progress_callback:
                    item_progress_callback(idx + 1, total, item)
                continue

            # Handle pause state
            while self._is_paused and not self._is_cancelled:
                await asyncio.sleep(0.5)

            if self._is_cancelled:
                item.status = "skipped"
                item.error = "Cancelled by user"
                if item_progress_callback:
                    item_progress_callback(idx + 1, total, item)
                continue

            item.status = "processing"
            if item_progress_callback:
                item_progress_callback(idx + 1, total, item)

            start_t = time.time()
            try:
                _, duration = await translate_image(
                    input_path=item.input_path,
                    source_lang=self.source_lang,
                    target_lang=self.target_lang,
                    engine=self.engine,
                    output_path=item.output_path,
                    model_dir=self.model_dir,
                    api_key=self.api_key,
                    cancel_check=lambda: self._is_cancelled,
                )
                item.status = "success"
                item.duration = duration

                if self.history_manager:
                    self.history_manager.add(
                        HistoryEntry(
                            input_path=str(item.input_path),
                            output_path=str(item.output_path),
                            source_lang=self.source_lang,
                            target_lang=self.target_lang,
                            engine=self.engine,
                            duration=duration,
                            success=True,
                        )
                    )

            except Exception as e:
                duration = time.time() - start_t
                item.status = "error"
                item.duration = duration
                item.error = str(e)
                logger.warning("Batch item %s failed: %s", item.input_path.name, e)

                if self.history_manager:
                    self.history_manager.add(
                        HistoryEntry(
                            input_path=str(item.input_path),
                            output_path=None,
                            source_lang=self.source_lang,
                            target_lang=self.target_lang,
                            engine=self.engine,
                            duration=duration,
                            success=False,
                            error=str(e),
                        )
                    )

            if item_progress_callback:
                item_progress_callback(idx + 1, total, item)

        return self.items

    def export_log(self, destination: Path) -> Path:
        """Export batch processing summary and results to a text report."""
        destination.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            f"=== LumieTL Batch Translation Report ===",
            f"Input Directory:  {self.input_dir}",
            f"Output Directory: {self.output_dir}",
            f"Source Language:  {self.source_lang}",
            f"Target Language:  {self.target_lang}",
            f"Engine:           {self.engine}",
            f"Total Files:      {len(self.items)}",
            "",
            f"{'File Name':<35} | {'Status':<10} | {'Duration':<8} | {'Error'}",
            "-" * 80,
        ]

        for item in self.items:
            dur = f"{item.duration:.2f}s" if item.duration > 0 else "—"
            err = item.error if item.error else ""
            lines.append(f"{item.input_path.name:<35} | {item.status:<10} | {dur:<8} | {err}")

        lines.append("-" * 80)
        successful = sum(1 for i in self.items if i.status == "success")
        failed = sum(1 for i in self.items if i.status == "error")
        skipped = sum(1 for i in self.items if i.status == "skipped")
        lines.append(f"Summary: {successful} succeeded, {failed} failed, {skipped} skipped.")

        destination.write_text("\n".join(lines), encoding="utf-8")
        return destination
