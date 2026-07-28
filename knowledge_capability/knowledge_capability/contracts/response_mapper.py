from __future__ import annotations

from dataclasses import asdict
from typing import Any

from knowledge_capability.contracts.error_mapper import BusinessAgentErrorMapper
from knowledge_capability.contracts.models import KnowledgeResponse
from knowledge_capability.contracts.validator import BusinessAgentContractValidator
from knowledge_capability.contracts.version import CONTRACT_VERSION


class BusinessAgentResponseMapper:
    @staticmethod
    def from_knowledge_response(response: KnowledgeResponse) -> dict[str, Any]:
        payload = {
            "request_id": response.request_id,
            "service_id": response.service_id,
            "success": response.success,
            "result": response.result,
            "evidence": [asdict(item) for item in response.evidence],
            "trace": [asdict(item) for item in response.trace],
            "warnings": list(response.warnings),
            "error": BusinessAgentErrorMapper.to_dict(response.error),
            "contract_version": CONTRACT_VERSION,
            "created_at": response.created_at,
        }
        BusinessAgentContractValidator.validate_response(payload)
        return payload
