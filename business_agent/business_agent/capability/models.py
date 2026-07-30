from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CapabilityInvocation:
    capability_type: str
    binding_name: str
    operation: str
    request_id: str
    trace_id: str
    service_id: str
    service_version: str
    schema_version: str
    payload: dict[str, Any]
    attempt: int = 1


@dataclass
class CapabilityResult:
    capability_type: str
    binding_name: str
    operation: str
    status: str
    request_id: str
    response_id: str = ""
    trace_id: str = ""
    items: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    degraded: bool = False
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def successful(self) -> bool:
        return self.status in {"success", "partial_success", "no_result"}
