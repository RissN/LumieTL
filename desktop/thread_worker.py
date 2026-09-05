"""Thread worker module for executing heavy background tasks without blocking the Qt GUI."""

import asyncio
import inspect
from typing import Any, Callable
from PySide6.QtCore import QThread, Signal


class Worker(QThread):
    """
    Generic QThread worker.
    Executes a callable (sync or async coroutine function) in a background thread,
    emitting Qt signals for progress, completion, and error states.
    """

    progress = Signal(int, int, str)  # current, total, message
    finished = Signal(object)  # result payload
    error = Signal(str)  # error description

    def __init__(self, fn: Callable, *args: Any, **kwargs: Any):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self._cancelled = False

    def run(self) -> None:
        try:
            extra_kwargs = {
                "progress_callback": self._emit_progress,
                "cancel_check": self._is_cancelled,
            }

            # Only pass progress_callback / cancel_check if accepted by the target function
            sig = inspect.signature(self.fn)
            passed_kwargs = dict(self.kwargs)
            for key in ["progress_callback", "cancel_check"]:
                if key in sig.parameters:
                    passed_kwargs[key] = extra_kwargs[key]

            # Execute async coroutine functions or normal callables
            if inspect.iscoroutinefunction(self.fn):
                result = asyncio.run(self.fn(*self.args, **passed_kwargs))
            else:
                result = self.fn(*self.args, **passed_kwargs)

            if not self._cancelled:
                self.finished.emit(result)
        except Exception as e:
            if not self._cancelled:
                self.error.emit(str(e))

    def cancel(self) -> None:
        """Flag the worker as cancelled."""
        self._cancelled = True

    def _is_cancelled(self) -> bool:
        return self._cancelled

    def _emit_progress(self, current: int, total: int, msg: str = "") -> None:
        if not self._cancelled:
            self.progress.emit(current, total, msg)
