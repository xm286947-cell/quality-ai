from __future__ import annotations

from typing import Any

from business_agent.models import RuntimeContext
from business_agent.trace.manager import TraceManager
from business_agent.workflow.handler_registry import HandlerRegistry


class WorkflowEngine:
    """Sequential configuration-driven workflow executor for V1.1 M1."""

    def __init__(self, registry: HandlerRegistry, trace: TraceManager) -> None:
        self.registry = registry
        self.trace = trace

    def execute(self, context: RuntimeContext) -> dict[str, Any]:
        output: dict[str, Any] = {}
        for node in context.profile.workflow:
            if not node.enabled:
                self.trace.node_skipped(node)
                continue
            self.trace.node_started(node)
            try:
                handler = self.registry.resolve(node.handler)
                result = handler(context, node)
                if not isinstance(result, dict):
                    raise TypeError(f"Handler必须返回dict: {node.handler}")
                context.node_results[node.id] = result
                context.data.update(result.get("context_updates") or {})
                output = result.get("output") or output
                self.trace.node_succeeded(node, result)
            except Exception as exc:
                self.trace.node_failed(node, exc)
                raise
        return output or {"node_results": context.node_results}
