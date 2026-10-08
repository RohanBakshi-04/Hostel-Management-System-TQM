"""Helper utilities and benchmark timers for Q05 Response Time verification.

TQM Goal: Q05 - Reduce Response Time.
Provides microsecond-accurate query profiling and execution timers.
"""

import time
from datetime import datetime
from typing import Callable, Any, Tuple


class LatencyTimer:
    """Microsecond-accurate stopwatch for benchmarking Q05 response times."""

    def __init__(self):
        self._start_time: float = 0.0
        self._end_time: float = 0.0

    def start(self) -> None:
        """Start the timer."""
        self._start_time = time.perf_counter()

    def stop(self) -> float:
        """Stop the timer and return elapsed time in milliseconds."""
        self._end_time = time.perf_counter()
        return (self._end_time - self._start_time) * 1000.0

    @classmethod
    def measure(cls, func: Callable, *args, **kwargs) -> Tuple[Any, float]:
        """Execute a callable function and measure its elapsed execution time.

        Returns:
            Tuple[Any, float]: (function_result, elapsed_ms)
        """
        timer = cls()
        timer.start()
        result = func(*args, **kwargs)
        elapsed_ms = timer.stop()
        return result, elapsed_ms


def format_currency(amount: float) -> str:
    """Format numeric currency value to readable INR string."""
    return f"Rs. {amount:,.2f}"


def format_timestamp(dt_str: str) -> str:
    """Format ISO timestamp to readable presentation date."""
    if not dt_str:
        return "-"
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%d %b %Y, %I:%M %p")
    except Exception:
        return dt_str


def generate_complaint_id(seq: int) -> str:
    """Generate standardized complaint ticket ID."""
    return f"CMP-{seq:04d}"
