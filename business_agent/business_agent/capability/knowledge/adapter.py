from __future__ import annotations

from typing import Any

from ..binding import CapabilityBinding
from ..errors import CapabilityValidationError
from ..gateway import CapabilityGateway
from ..models import CapabilityInvocation, CapabilityResult


_ALLOWED_OPERATIONS = {
    "query_knowledge",
    "describe_service",
    "health_check",
}


class KnowledgeContractAdapter:
    CONTRACT_VERSION = "1.0"

    def build_request(
        self,
        binding: CapabilityBinding,
        invocation: CapabilityInvocation,
        context: Any,
    ) -> dict[str, Any]:
        if binding.operation not in _ALLOWED_OPERATIONS:
            raise CapabilityValidationError(
                f"unsupported knowledge operation: {binding.operation}"
            )

        profile = getattr(context, "profile", None)
        request = getattr(context, "request", None)
        inputs = dict(getattr(request, "inputs", {}) or {})
        data = getattr(context, "data", {}) or {}
        identity = data.get("identity") or {}

        envelope: dict[str, Any] = {
            "contract_version": self.CONTRACT_VERSION,
            "request_id": invocation.request_id,
            "trace_id": invocation.trace_id,
            "operation": binding.operation,
            "service": {
                "service_id": binding.service_id,
                "service_version": binding.service_version,
                "schema_version": binding.schema_version,
            },
            "caller": {
                "agent_id": str(getattr(profile, "agent_id", "")),
                "agent_version": str(getattr(profile, "version", "")),
                "capability_id": binding.binding_name,
                "execution_id": str(identity.get("execution_id", "")),
            },
            "query": dict(invocation.payload.get("query") or inputs),
            "filters": dict(invocation.payload.get("filters") or {}),
            "requested_fields": list(
                invocation.payload.get("requested_fields")
                or binding.requested_fields
            ),
            "context": dict(invocation.payload.get("context") or {}),
            "options": {
                **binding.default_options,
                **dict(invocation.payload.get("options") or {}),
            },
            "trace_options": dict(
                invocation.payload.get("trace_options")
                or {"enabled": True, "level": "standard"}
            ),
        }
        return envelope

    def parse_response(
        self,
        binding: CapabilityBinding,
        invocation: CapabilityInvocation,
        raw: dict[str, Any],
    ) -> CapabilityResult:
        if not isinstance(raw, dict):
            raise CapabilityValidationError("knowledge response must be a mapping")

        contract_version = str(raw.get("contract_version", ""))
        if contract_version and contract_version != self.CONTRACT_VERSION:
            raise CapabilityValidationError(
                f"unsupported contract_version: {contract_version}"
            )

        status = str(raw.get("status", "")).lower()
        if status not in {"success", "partial_success", "no_result", "failed"}:
            raise CapabilityValidationError(f"invalid knowledge status: {status!r}")

        result_block = raw.get("result") or {}
        items = result_block.get("items", raw.get("items", [])) or []
        evidence = result_block.get("evidence", raw.get("evidence", [])) or []

        normalized_items = [self._normalize_item(item) for item in items]
        normalized_evidence = [
            dict(item) for item in evidence if isinstance(item, dict)
        ]

        warnings = self._normalize_messages(raw.get("warnings", []))
        errors = self._normalize_messages(raw.get("errors", []))
        if raw.get("error"):
            errors.extend(self._normalize_messages([raw["error"]]))

        return CapabilityResult(
            capability_type="knowledge",
            binding_name=binding.binding_name,
            operation=binding.operation,
            status=status,
            request_id=str(raw.get("request_id") or invocation.request_id),
            response_id=str(raw.get("response_id", "")),
            trace_id=str(
                raw.get("knowledge_trace_id")
                or raw.get("trace_id")
                or invocation.trace_id
            ),
            items=normalized_items,
            evidence=normalized_evidence,
            warnings=warnings,
            errors=errors,
            metadata={
                "contract_version": contract_version or self.CONTRACT_VERSION,
                "service_id": binding.service_id,
                "service_version": binding.service_version,
                "schema_version": binding.schema_version,
                **dict(raw.get("metadata") or {}),
            },
            degraded=status == "partial_success",
            raw=raw,
        )

    @staticmethod
    def _normalize_item(item: Any) -> dict[str, Any]:
        if not isinstance(item, dict):
            raise CapabilityValidationError("knowledge result item must be a mapping")
        score = item.get("score")
        if score is not None:
            score = float(score)
            if score < 0.0 or score > 1.0:
                raise CapabilityValidationError("knowledge item score must be 0.0-1.0")
        return {
            "knowledge_id": str(item.get("knowledge_id", "")),
            "knowledge_version": str(item.get("knowledge_version", "")),
            "knowledge_type": str(item.get("knowledge_type", "")),
            "rank": item.get("rank"),
            "title": str(item.get("title", "")),
            "summary": str(item.get("summary", "")),
            "score": score,
            "fields": dict(item.get("fields") or {}),
            "evidence_refs": list(item.get("evidence_refs") or []),
        }

    @staticmethod
    def _normalize_messages(messages: Any) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for message in messages or []:
            if isinstance(message, dict):
                normalized.append(dict(message))
            else:
                normalized.append({"message": str(message)})
        return normalized


class KnowledgeGateway(CapabilityGateway):
    capability_type = "knowledge"

    def __init__(self, client: Any) -> None:
        super().__init__(client)
        self.adapter = KnowledgeContractAdapter()

    def build_request(
        self,
        binding: CapabilityBinding,
        invocation: CapabilityInvocation,
        context: Any,
    ) -> dict[str, Any]:
        return self.adapter.build_request(binding, invocation, context)

    def parse_response(
        self,
        binding: CapabilityBinding,
        invocation: CapabilityInvocation,
        raw: dict[str, Any],
    ) -> CapabilityResult:
        return self.adapter.parse_response(binding, invocation, raw)
