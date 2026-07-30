from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .errors import CapabilityValidationError


@dataclass(frozen=True)
class CapabilityRuntimePolicy:
    timeout_ms: int = 30000
    max_attempts: int = 1
    backoff_ms: int = 0
    allow_degraded_result: bool = True
    fail_on_no_result: bool = False
    fail_on_partial_success: bool = False

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> "CapabilityRuntimePolicy":
        raw = raw or {}
        retry = raw.get("retry") or {}
        policy = cls(
            timeout_ms=int(raw.get("timeout_ms", 30000)),
            max_attempts=int(retry.get("max_attempts", raw.get("max_attempts", 1))),
            backoff_ms=int(retry.get("backoff_ms", raw.get("backoff_ms", 0))),
            allow_degraded_result=bool(raw.get("allow_degraded_result", True)),
            fail_on_no_result=bool(raw.get("fail_on_no_result", False)),
            fail_on_partial_success=bool(raw.get("fail_on_partial_success", False)),
        )
        if policy.timeout_ms <= 0:
            raise CapabilityValidationError("timeout_ms must be greater than zero")
        if policy.max_attempts <= 0:
            raise CapabilityValidationError("max_attempts must be greater than zero")
        if policy.backoff_ms < 0:
            raise CapabilityValidationError("backoff_ms cannot be negative")
        return policy


@dataclass(frozen=True)
class CapabilityBinding:
    binding_name: str
    capability_type: str
    service_id: str
    service_version: str
    schema_version: str
    operation: str
    requested_fields: tuple[str, ...] = ()
    default_options: dict[str, Any] = field(default_factory=dict)
    runtime_policy: CapabilityRuntimePolicy = field(default_factory=CapabilityRuntimePolicy)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(
        cls,
        binding_name: str,
        capability_type: str,
        raw: dict[str, Any],
    ) -> "CapabilityBinding":
        required = ("service_id", "service_version", "schema_version", "operation")
        missing = [name for name in required if not raw.get(name)]
        if missing:
            raise CapabilityValidationError(
                f"binding '{binding_name}' missing required fields: {', '.join(missing)}"
            )
        return cls(
            binding_name=binding_name,
            capability_type=capability_type,
            service_id=str(raw["service_id"]),
            service_version=str(raw["service_version"]),
            schema_version=str(raw["schema_version"]),
            operation=str(raw["operation"]),
            requested_fields=tuple(str(v) for v in raw.get("requested_fields", [])),
            default_options=dict(raw.get("default_options") or {}),
            runtime_policy=CapabilityRuntimePolicy.from_dict(raw.get("runtime_policy")),
            metadata=dict(raw.get("metadata") or {}),
        )
