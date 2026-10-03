"""Background worker thread pool utility for non-blocking GUI operations."""

import logging
import os
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Shared daemon thread pool executor for background tasks (PDF generation, heavy operations)
_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="wellcare_worker")


def run_async(
    task_fn: Callable[..., T],
    *args: Any,
    on_success: Callable[[T], None] | None = None,
    on_error: Callable[[Exception], None] | None = None,
    master_widget: Any = None,
    **kwargs: Any,
) -> None:
    """Executes task_fn(*args, **kwargs) in a background worker thread.

    Upon completion, marshals on_success(result) or on_error(exception) back
    to the Tkinter main UI thread via master_widget.after(0, ...) if provided.
    Under pytest, runs synchronously to ensure deterministic test assertions.
    """
    if os.environ.get("PYTEST_CURRENT_TEST"):
        try:
            result = task_fn(*args, **kwargs)
            if on_success:
                on_success(result)
        except Exception as exc:
            logger.error("Error in task: %s", exc, exc_info=True)
            if on_error:
                on_error(exc)
        return

    def _worker() -> None:
        try:
            result = task_fn(*args, **kwargs)
            if on_success:
                if master_widget and hasattr(master_widget, "after"):
                    try:
                        master_widget.after(0, lambda res=result: on_success(res))
                    except Exception:
                        on_success(result)
                else:
                    on_success(result)
        except Exception as exc:
            logger.error("Error in background worker: %s", exc, exc_info=True)
            if on_error:
                if master_widget and hasattr(master_widget, "after"):
                    try:
                        master_widget.after(0, lambda e=exc: on_error(e))
                    except Exception:
                        on_error(exc)
                else:
                    on_error(exc)

    _EXECUTOR.submit(_worker)


def shutdown_executor(wait: bool = False) -> None:
    """Shut down the background worker thread pool."""
    _EXECUTOR.shutdown(wait=wait, cancel_futures=True)
