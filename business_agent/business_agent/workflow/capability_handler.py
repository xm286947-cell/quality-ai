from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from business_agent.capability.models import CapabilityResult
from business_agent.capability.runtime_binding import RuntimeCapabilityBinding
from business_agent.models import RuntimeContext, WorkflowNode
from business_agent.workflow.node_result import NodeResult, NodeStatus


class CapabilityNodeConfigurationError(ValueError):
    """Raised when a capability workflow node is missing required configuration."""


@dataclass
class CapabilityNodeHandler:
    """Workflow handler that delegates a node to RuntimeCapabilityBinding."""

    runtime_binding: RuntimeCapabilityBinding

    def __call__(self, context: RuntimeContext, node: WorkflowNode) -> NodeResult:
        capability_type = self._required(node, "capability_type")
        binding_name = self._required(node, "binding_name")
        payload = self._build_payload(context, node)

        result = self.runtime_binding.invoke(
            context,
            capability_type=capability_type,
            binding_name=binding_name,
            payload=payload,
        )
        return capability_result_to_node_result(node, result)

    @staticmethod
    def _required(node: WorkflowNode, name: str) -> str:
        value = str(node.config.get(name, "")).strip()
        if not value:
            raise CapabilityNodeConfigurationError(
                f"Capability node '{node.id}' missing config.{name}"
            )
        return value

    @staticmethod
    def _build_payload(
        context: RuntimeContext,
        node: WorkflowNode,
    ) -> dict[str, Any]:
        configured = node.config.get("payload") or {}
        if not isinstance(configured, dict):
            raise CapabilityNodeConfigurationError(
                f"Capability node '{node.id}' config.payload must be a mapping"
            )

        payload = dict(configured)
        if bool(node.config.get("include_inputs", True)):
            payload.setdefault("inputs", dict(context.request.inputs))
        if bool(node.config.get("include_context", False)):
            payload.setdefault("context", dict(context.data))
        return payload


def capability_result_to_node_result(
    node: WorkflowNode,
    result: CapabilityResult,
) -> NodeResult:
    """Normalize Capability Contract statuses into Workflow NodeResult."""

    status_map = {
        "success": NodeStatus.SUCCESS,
        "partial_success": NodeStatus.PARTIAL_SUCCESS,
        "no_result": NodeStatus.NO_RESULT,
        "failed": NodeStatus.FAILED,
    }
    try:
        node_status = status_map[result.status]
    except KeyError as exc:
        raise ValueError(f"Unsupported capability status: {result.status}") from exc

    output = {
        "capability_type": result.capability_type,
        "binding_name": result.binding_name,
        "operation": result.operation,
        "status": result.status,
        "items": list(result.items),
        "evidence": list(result.evidence),
        "metadata": dict(result.metadata),
        "degraded": bool(result.degraded),
    }
    trace = {
        "request_id": result.request_id,
        "response_id": result.response_id,
        "trace_id": result.trace_id,
    }
    context_updates = {
        "last_capability_result": output,
        f"capability_result.{node.id}": output,
    }

    error = None
    if node_status == NodeStatus.FAILED:
        error = {
            "type": "CapabilityFailed",
            "message": "; ".join(
                str(item.get("message", "")) for item in result.errors
            ) or "Capability returned failed status",
            "details": list(result.errors),
        }

    return NodeResult(
        node_id=node.id,
        status=node_status,
        output=output,
        context_updates=context_updates,
        warnings=list(result.warnings),
        error=error,
        metrics={
            "item_count": len(result.items),
            "evidence_count": len(result.evidence),
            "warning_count": len(result.warnings),
            "error_count": len(result.errors),
        },
        trace=trace,
    )
