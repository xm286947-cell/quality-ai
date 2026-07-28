from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from uuid import uuid4

from knowledge_capability.contracts.models import KnowledgeRequest
from knowledge_capability.contracts.validator import BusinessAgentContractValidator
from knowledge_capability.contracts.version import to_internal_contract_version


class BusinessAgentRequestMapper:
    @staticmethod
    def to_knowledge_request(payload: Mapping[str, Any]) -> KnowledgeRequest:
        BusinessAgentContractValidator.validate_request(payload)
        caller = dict(payload.get("caller") or {})
        caller.setdefault("type", "business_agent")
        return KnowledgeRequest(
            service_id=str(payload["service_id"]).strip(),
            query=dict(payload["query"]),
            request_id=str(payload.get("request_id") or "").strip() or uuid4().hex,
            filters=dict(payload.get("filters") or {}),
            requested_fields=list(payload.get("requested_fields") or []),
            options=dict(payload.get("options") or {}),
            caller=caller,
            contract_version=to_internal_contract_version(payload.get("contract_version", "V1.0")),
        )
