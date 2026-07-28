from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Iterable

from business_agent.contracts.execution import ExecutionContext, ExecutionTrace
from business_agent.handlers import ExecutionHandler


class PipelineExecutionError(RuntimeError):
    """Pipeline failure retaining the partial context and collected trace."""

    def __init__(
        self,
        message: str,
        *,
        context: ExecutionContext,
        trace: list[ExecutionTrace],
        failed_step: str,
        cause: Exception,
    ) -> None:
        super().__init__(message)
        self.context = context
        self.trace = trace
        self.failed_step = failed_step
        self.cause = cause


class ExecutionPipeline:
    """Sequential handler pipeline with step-level trace collection."""

    def __init__(self, handlers: Iterable[ExecutionHandler]) -> None:
        self._handlers = tuple(handlers)
        if not self._handlers:
            raise ValueError("execution pipeline requires at least one handler")
        names = [handler.name for handler in self._handlers]
        if len(names) != len(set(names)):
            raise ValueError("execution pipeline handler names must be unique")

    @property
    def handler_names(self) -> tuple[str, ...]:
        return tuple(handler.name for handler in self._handlers)

    def run(self, context: ExecutionContext) -> tuple[ExecutionContext, list[ExecutionTrace]]:
        traces: list[ExecutionTrace] = []
        current = context
        for handler in self._handlers:
            started_at = datetime.now(timezone.utc)
            started = perf_counter()
            try:
                current = handler.handle(current)
            except Exception as exc:
                trace = ExecutionTrace(
                    step=handler.name,
                    status="failed",
                    started_at=started_at,
                    finished_at=datetime.now(timezone.utc),
                    duration_ms=(perf_counter() - started) * 1000,
                    metadata={"error_type": type(exc).__name__, "message": str(exc)},
                )
                traces.append(trace)
                raise PipelineExecutionError(
                    str(exc) or f"execution step failed: {handler.name}",
                    context=current,
                    trace=traces,
                    failed_step=handler.name,
                    cause=exc,
                ) from exc
            traces.append(
                ExecutionTrace(
                    step=handler.name,
                    status="success",
                    started_at=started_at,
                    finished_at=datetime.now(timezone.utc),
                    duration_ms=(perf_counter() - started) * 1000,
                    metadata={},
                )
            )
        return current, traces
