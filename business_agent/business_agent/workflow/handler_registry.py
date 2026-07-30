from __future__ import annotations

from collections.abc import Callable
from threading import RLock
from typing import Any

from business_agent.models import RuntimeContext, WorkflowNode
from business_agent.workflow.node_result import NodeResult

Handler = Callable[
    [RuntimeContext, WorkflowNode],
    NodeResult | dict[str, Any] | None,
]


class HandlerRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, Handler] = {}
        self._lock = RLock()

    def register(
        self,
        name: str,
        handler: Handler,
        *,
        overwrite: bool = False,
    ) -> None:
        key = str(name).strip()
        if not key:
            raise ValueError("handler name must not be empty")
        if not callable(handler):
            raise TypeError("handler must be callable")

        with self._lock:
            if key in self._handlers and not overwrite:
                raise ValueError(f"Workflow Handler already registered: {key}")
            self._handlers[key] = handler

    def contains(self, name: str) -> bool:
        with self._lock:
            return name in self._handlers

    def resolve(self, name: str) -> Handler:
        with self._lock:
            try:
                return self._handlers[name]
            except KeyError as exc:
                raise LookupError(f"Workflow Handler is not registered: {name}") from exc

    def names(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(sorted(self._handlers))
