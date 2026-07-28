from __future__ import annotations

from business_agent.contracts.execution import ExecutionContext
from business_agent.handlers.base import ExecutionHandler


class ContextHandler(ExecutionHandler):
    name = "context"

    def handle(self, context: ExecutionContext) -> ExecutionContext:
        context.variables.setdefault("context_ready", True)
        return context
