from __future__ import annotations

from typing import Any, Protocol

from business_agent.models import RuntimeContext, WorkflowNode
from business_agent.workflow.handler_registry import HandlerRegistry
from business_agent.workflow.node_result import NodeResult, NodeStatus
from business_agent.workflow.policy import NodeRuntimePolicy


class TracePort(Protocol):
    def node_started(self, node: WorkflowNode) -> None: ...
    def node_succeeded(self, node: WorkflowNode, result: dict[str, Any]) -> None: ...
    def node_skipped(self, node: WorkflowNode) -> None: ...
    def node_failed(self, node: WorkflowNode, exc: Exception) -> None: ...


class NullTrace:
    def node_started(self, node: WorkflowNode) -> None:
        return None

    def node_succeeded(self, node: WorkflowNode, result: dict[str, Any]) -> None:
        return None

    def node_skipped(self, node: WorkflowNode) -> None:
        return None

    def node_failed(self, node: WorkflowNode, exc: Exception) -> None:
        return None


class WorkflowExecutionError(RuntimeError):
    pass


class WorkflowEngine:
    """Sequential, configuration-driven Workflow Core for V1.3 M1 P02."""

    def __init__(
        self,
        registry: HandlerRegistry,
        trace: TracePort | None = None,
    ) -> None:
        self.registry = registry
        self.trace = trace or NullTrace()

    def execute(self, context: RuntimeContext) -> dict[str, Any]:
        final_output: dict[str, Any] = {}

        for node in context.profile.workflow:
            if not node.enabled:
                result = NodeResult(
                    node_id=node.id,
                    status=NodeStatus.SKIPPED,
                )
                context.node_results[node.id] = result.to_dict()
                self.trace.node_skipped(node)
                continue

            policy = NodeRuntimePolicy.from_mapping(node.runtime_policy)
            self.trace.node_started(node)

            try:
                handler = self.registry.resolve(node.handler)
                raw_result = handler(context, node)
                result = NodeResult.from_handler_result(
                    node_id=node.id,
                    value=raw_result,
                )

                if (
                    result.status == NodeStatus.PARTIAL_SUCCESS
                    and not policy.allow_partial_success
                ):
                    raise WorkflowExecutionError(
                        f"Node partial success is forbidden by policy: {node.id}"
                    )

                result_payload = result.to_dict()
                context.node_results[node.id] = result_payload
                context.data.update(result.context_updates)

                if result.output:
                    final_output = result.output

                self.trace.node_succeeded(node, result_payload)

                if result.status == NodeStatus.FAILED:
                    self._handle_failed_result(node, result, policy)

            except Exception as exc:
                self.trace.node_failed(node, exc)
                failed = NodeResult(
                    node_id=node.id,
                    status=NodeStatus.FAILED,
                    error={
                        "type": type(exc).__name__,
                        "message": str(exc),
                    },
                )
                context.node_results[node.id] = failed.to_dict()

                if policy.on_failure == "continue":
                    continue
                if policy.on_failure == "skip":
                    context.node_results[node.id] = NodeResult(
                        node_id=node.id,
                        status=NodeStatus.SKIPPED,
                        warnings=[f"Skipped after failure: {exc}"],
                    ).to_dict()
                    continue
                raise WorkflowExecutionError(
                    f"Workflow node failed: {node.id}"
                ) from exc

        return final_output or {"node_results": context.node_results}

    @staticmethod
    def _handle_failed_result(
        node: WorkflowNode,
        result: NodeResult,
        policy: NodeRuntimePolicy,
    ) -> None:
        if policy.on_failure == "continue":
            return
        if policy.on_failure == "skip":
            return
        message = (result.error or {}).get("message", "node returned failed status")
        raise WorkflowExecutionError(f"Workflow node failed: {node.id}: {message}")
