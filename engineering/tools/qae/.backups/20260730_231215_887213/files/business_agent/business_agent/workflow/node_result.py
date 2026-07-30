from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class NodeStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass
class NodeResult:
    node_id: str
    status: NodeStatus
    output: dict[str, Any] = field(default_factory=dict)
    context_updates: dict[str, Any] = field(default_factory=dict)
    warnings: list[dict[str, Any] | str] = field(default_factory=list)
    error: dict[str, Any] | None = None
    metrics: dict[str, Any] = field(default_factory=dict)
    trace: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.node_id.strip():
            raise ValueError("node_id must not be empty")
        if self.status == NodeStatus.FAILED and self.error is None:
            raise ValueError("failed NodeResult must contain error")
        if self.status != NodeStatus.FAILED and self.error is not None:
            raise ValueError("only failed NodeResult may contain error")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        payload = asdict(self)
        payload["status"] = self.status.value
        return payload

    @classmethod
    def from_handler_result(
        cls,
        *,
        node_id: str,
        value: "NodeResult | dict[str, Any] | None",
    ) -> "NodeResult":
        if isinstance(value, cls):
            if value.node_id != node_id:
                raise ValueError(
                    f"NodeResult node_id mismatch: expected={node_id} actual={value.node_id}"
                )
            value.validate()
            return value

        if value is None:
            return cls(node_id=node_id, status=NodeStatus.SUCCESS)

        if not isinstance(value, dict):
            raise TypeError("Workflow handler must return NodeResult, dict or None")

        status_value = value.get("status", NodeStatus.SUCCESS.value)
        try:
            status = NodeStatus(status_value)
        except ValueError as exc:
            raise ValueError(f"Unsupported node status: {status_value}") from exc

        result = cls(
            node_id=node_id,
            status=status,
            output=dict(value.get("output") or {}),
            context_updates=dict(value.get("context_updates") or {}),
            warnings=list(value.get("warnings") or []),
            error=value.get("error"),
            metrics=dict(value.get("metrics") or {}),
            trace=dict(value.get("trace") or {}),
        )
        result.validate()
        return result
