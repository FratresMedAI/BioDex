"""Progress helpers with ETA estimation for batch and video pipelines."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class ProgressTracker:
    """Rolling progress tracker with ETA for long-running jobs."""

    total: int
    _start: float = field(default_factory=time.perf_counter)
    _last_fraction: float = 0.0
    _durations: list[float] = field(default_factory=list)
    _last_tick: float = field(default_factory=time.perf_counter)

    def tick(self, current: int, message: str) -> tuple[float, str]:
        """
        Record progress for ``current`` (1-based index) and return fraction + ETA text.

        Returns:
            ``(fraction, message_with_eta)`` where fraction is in ``[0.0, 1.0]``.
        """
        now = time.perf_counter()
        if current > 0:
            self._durations.append(now - self._last_tick)
            if len(self._durations) > 20:
                self._durations.pop(0)
        self._last_tick = now

        fraction = current / self.total if self.total else 1.0
        self._last_fraction = fraction
        eta = self._format_eta(current)
        if eta:
            return fraction, f"{message} — ETA {eta}"
        return fraction, message

    def _format_eta(self, current: int) -> str:
        if current <= 0 or not self._durations or self.total <= current:
            return ""
        avg = sum(self._durations) / len(self._durations)
        remaining = (self.total - current) * avg
        if remaining < 60:
            return f"{remaining:.0f}s"
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        return f"{minutes}m {seconds}s"

    @property
    def elapsed_s(self) -> float:
        return time.perf_counter() - self._start

    @property
    def fraction(self) -> float:
        return self._last_fraction


ProgressCallback = Callable[[int, int, str, float], None]


def make_tracked_callback(
    callback: ProgressCallback | None,
    total: int,
) -> tuple[ProgressTracker, Callable[[int, str], None]]:
    """Build a tracker and a simplified ``(current, message)`` hook for inner loops."""
    tracker = ProgressTracker(total=total)

    def emit(current: int, message: str) -> None:
        fraction, enriched = tracker.tick(current, message)
        if callback:
            callback(current, total, enriched, fraction)

    return tracker, emit


__all__ = ["ProgressCallback", "ProgressTracker", "make_tracked_callback"]
