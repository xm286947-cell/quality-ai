from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol
from uuid import uuid4

from knowledge_capability.contracts import ContractError, KnowledgeResponse
from knowledge_capability.contracts.request_mapper import BusinessAgentRequestMapper
from knowledge_capability.contracts.response_mapper import BusinessAgentResponseMapper
from knowledge_capability.contracts.validator import ContractValidationError
from knowledge_capability.contracts.version import CONTRACT_VERSION


class RuntimeExecutor(Protocol):
    def execute(self, request): ...


class BusinessAgentAdapter:
    """Frozen V1.0 in-process integration boundary used by Business Agent."""

    def __init__(self, runtime: RuntimeExecutor) -> None:
        self.runtime = runtime

    def execute(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        try:
            request = BusinessAgentRequestMapper.to_knowledge_request(payload)
            response = self.runtime.execute(request)
        except ContractValidationError as exc:
            response = self._invalid_request_response(payload, exc)
        return BusinessAgentResponseMapper.from_knowledge_response(response)

    def query(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self.execute(payload)

    @staticmethod
    def _invalid_request_response(payload: Mapping[str, Any] | Any, error: Exception) -> KnowledgeResponse:
        mapping = payload if isinstance(payload, Mapping) else {}
        return KnowledgeResponse(
            request_id=str(mapping.get("request_id") or uuid4().hex),
            service_id=str(mapping.get("service_id") or "unknown"),
            error=ContractError(
                code="INVALID_REQUEST",
                message=str(error),
                details={"contract_version": CONTRACT_VERSION},
                retryable=False,
            ),
        )
