"""Micro-animation utilities for WellCare UI components."""

from collections.abc import Callable
from typing import Any


def animate_count_up(
    widget: Any,
    target_val: int,
    current_val: int = 0,
    steps: int = 15,
    delay_ms: int = 20,
    formatter: Callable[[int], str] | None = None,
) -> None:
    """Animate a numeric metric counter from current_val to target_val."""
    if current_val >= target_val:
        text = formatter(target_val) if formatter else str(target_val)
        widget.configure(text=text)
        return

    increment = max(1, (target_val - current_val) // steps)
    next_val = min(target_val, current_val + increment)

    text = formatter(next_val) if formatter else str(next_val)
    widget.configure(text=text)

    if next_val < target_val:
        widget.after(
            delay_ms,
            lambda: animate_count_up(
                widget,
                target_val,
                next_val,
                steps,
                delay_ms,
                formatter,
            ),
        )
