from __future__ import annotations

import time
import uuid
from abc import ABC, abstractmethod
from typing import Any

from .binding import CapabilityBinding
from .errors import CapabilityInvocationError, CapabilityValidationError
from .models import CapabilityInvocation, CapabilityResult


class CapabilityGateway(ABC):
    """Base gateway implementing retry, policy, and context persistence."""

    capability_type = "generic"

    def __init__(self, client: Any) -> None:
        self.client = client

    def invoke(
        self,
        binding: CapabilityBinding,
        *,
        context: Any,
        payload: dict[str, Any] | None = None,
    ) -> CapabilityResult:
        request_id = self._request_id(context)
        trace_id = self._trace_id(context)
        policy = binding.runtime_policy
        last_error: Exception | None = None

        for attempt in range(1, policy.max_attempts + 1):
            invocation = CapabilityInvocation(
                capability_type=binding.capability_type,
                binding_name=binding.binding_name,
                operation=binding.operation,
                request_id=request_id,
                trace_id=trace_id,
                service_id=binding.service_id,
                service_version=binding.service_version,
                schema_version=binding.schema_version,
                payload=dict(payload or {}),
                attempt=attempt,
            )
            try:
                envelope = self.build_request(binding, invocation, context)
                raw = self.client.invoke(
                    binding.operation,
                    envelope,
                    timeout_ms=policy.timeout_ms,
                )
                result = self.parse_response(binding, invocation, raw)
                self._enforce_policy(binding, result)
                self.store_result(context, invocation, result)
                return result
            except CapabilityInvocationError as exc:
                last_error = exc
                if not exc.retryable or attempt >= policy.max_attempts:
                    break
                if policy.backoff_ms:
                    time.sleep(policy.backoff_ms / 1000)
            except (CapabilityValidationError, ValueError, TypeError):
                raise

        assert last_error is not None
        failed = CapabilityResult(
            capability_type=binding.capability_type,
            binding_name=binding.binding_name,
            operation=binding.operation,
            status="failed",
            request_id=request_id,
            trace_id=trace_id,
            errors=[{
                "code": "CAPABILITY_INVOCATION_FAILED",
                "message": str(last_error),
                "retryable": bool(getattr(last_error, "retryable", False)),
            }],
        )
        self.store_result(
            context,
            CapabilityInvocation(
                capability_type=binding.capability_type,
                binding_name=binding.binding_name,
                operation=binding.operation,
                request_id=request_id,
                trace_id=trace_id,
                service_id=binding.service_id,
                service_version=binding.service_version,
                schema_version=binding.schema_version,
                payload=dict(payload or {}),
            ),
            failed,
        )
        if policy.allow_degraded_result:
            failed.status = "partial_success"
            failed.degraded = True
            failed.warnings.append({
                "code": "CAPABILITY_DEGRADED",
                "message": str(last_error),
            })
            return failed
        raise last_error

    @abstractmethod
    def build_request(
        self,
        binding: CapabilityBinding,
        invocation: CapabilityInvocation,
        context: Any,
    ) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def parse_response(
        self,
        binding: CapabilityBinding,
        invocation: CapabilityInvocation,
        raw: dict[str, Any],
    ) -> CapabilityResult:
        raise NotImplementedError

    def store_result(
        self,
        context: Any,
        invocation: CapabilityInvocation,
        result: CapabilityResult,
    ) -> None:
        data = self._context_data(context)
        capabilities = data.setdefault("capabilities", {})
        bucket = capabilities.setdefault(binding_key(result.capability_type), {})
        bucket.setdefault("invocations", []).append({
            "binding_name": invocation.binding_name,
            "operation": invocation.operation,
            "request_id": invocation.request_id,
            "trace_id": invocation.trace_id,
            "service_id": invocation.service_id,
            "service_version": invocation.service_version,
            "schema_version": invocation.schema_version,
            "attempt": invocation.attempt,
        })
        bucket.setdefault("items", []).extend(result.items)
        bucket.setdefault("evidence", []).extend(result.evidence)
        bucket.setdefault("warnings", []).extend(result.warnings)
        bucket.setdefault("errors", []).extend(result.errors)
        bucket["last_status"] = result.status
        bucket["degraded"] = bool(bucket.get("degraded") or result.degraded)

    @staticmethod
    def _context_data(context: Any) -> dict[str, Any]:
        data = getattr(context, "data", None)
        if isinstance(data, dict):
            return data
        if isinstance(context, dict):
            return context
        raise CapabilityValidationError("runtime context must expose mutable 'data'")

    @staticmethod
    def _request_id(context: Any) -> str:
        request = getattr(context, "request", None)
        value = getattr(request, "request_id", "") if request is not None else ""
        return value or f"CAP-{uuid.uuid4().hex[:12].upper()}"

    @staticmethod
    def _trace_id(context: Any) -> str:
        data = CapabilityGateway._context_data(context)
        identity = data.get("identity") or {}
        return str(identity.get("trace_id") or data.get("trace_id") or "")

    @staticmethod
    def _enforce_policy(
        binding: CapabilityBinding,
        result: CapabilityResult,
    ) -> None:
        policy = binding.runtime_policy
        if result.status == "partial_success":
            result.degraded = True
            if policy.fail_on_partial_success:
                raise CapabilityInvocationError(
                    "partial_success rejected by runtime policy",
                    retryable=False,
                )
        elif result.status == "no_result" and policy.fail_on_no_result:
            raise CapabilityInvocationError(
                "no_result rejected by runtime policy",
                retryable=False,
            )
        elif result.status == "failed":
            retryable = any(bool(e.get("retryable")) for e in result.errors)
            message = "; ".join(str(e.get("message", "")) for e in result.errors)
            raise CapabilityInvocationError(
                message or "capability returned failed status",
                retryable=retryable,
            )


def binding_key(capability_type: str) -> str:
    return capability_type.strip().lower()
