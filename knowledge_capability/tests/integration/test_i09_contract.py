from __future__ import annotations

import pytest

from knowledge_capability.contracts.request_mapper import BusinessAgentRequestMapper
from knowledge_capability.contracts.validator import BusinessAgentContractValidator, ContractValidationError


def _payload():
    return {
        "contract_version": "V1.0",
        "request_id": "req-i09",
        "service_id": "repeat_case_service",
        "query": {"text": "CAN接收拥堵导致重启"},
        "filters": {"product": "DCDC"},
        "options": {"top_k": 3},
        "caller": {"type": "business_agent", "agent_id": "repeat_case_agent"},
    }


def test_contract_accepts_frozen_v10_request():
    BusinessAgentContractValidator.validate_request(_payload())
    request = BusinessAgentRequestMapper.to_knowledge_request(_payload())
    assert request.request_id == "req-i09"
    assert request.contract_version == "1.0"
    assert request.caller["type"] == "business_agent"


def test_contract_rejects_unknown_version():
    payload = _payload()
    payload["contract_version"] = "V2.0"
    with pytest.raises(ContractValidationError):
        BusinessAgentContractValidator.validate_request(payload)


def test_contract_rejects_invalid_query_shape():
    payload = _payload()
    payload["query"] = "not-an-object"
    with pytest.raises(ContractValidationError):
        BusinessAgentContractValidator.validate_request(payload)
