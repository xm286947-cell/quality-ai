from __future__ import annotations

from collections.abc import Callable
from typing import Any

from business_agent.errors import WorkflowExecutionError
from business_agent.models import RuntimeContext, WorkflowNode

Handler = Callable[[RuntimeContext, WorkflowNode], dict[str, Any]]


class HandlerRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, Handler] = {}

    def register(self, name: str, handler: Handler) -> None:
        key = str(name).strip()
        if not key:
            raise ValueError("handler name不能为空")
        self._handlers[key] = handler

    def contains(self, name: str) -> bool:
        return name in self._handlers

    def resolve(self, name: str) -> Handler:
        try:
            return self._handlers[name]
        except KeyError as exc:
            raise WorkflowExecutionError(f"未注册Workflow Handler: {name}") from exc
