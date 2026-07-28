from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Iterator

from knowledge_capability.contracts import TraceEntry


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class TraceManager:
    def __init__(self) -> None:
        self.entries: list[TraceEntry] = []

    def record(self, stage: str, component: str, status: str = "success", details: dict[str, Any] | None = None) -> None:
        now = _now()
        self.entries.append(TraceEntry(stage=stage, component=component, status=status, started_at=now, finished_at=now, details=details or {}))

    @contextmanager
    def step(self, stage: str, component: str, details: dict[str, Any] | None = None) -> Iterator[None]:
        started_at = _now()
        started = perf_counter()
        try:
            yield
        except Exception as exc:
            duration_ms = round((perf_counter() - started) * 1000, 3)
            self.entries.append(TraceEntry(stage=stage, component=component, status="failed", started_at=started_at, finished_at=_now(), details={**(details or {}), "duration_ms": duration_ms, "error_type": type(exc).__name__}))
            raise
        else:
            duration_ms = round((perf_counter() - started) * 1000, 3)
            self.entries.append(TraceEntry(stage=stage, component=component, status="success", started_at=started_at, finished_at=_now(), details={**(details or {}), "duration_ms": duration_ms}))
