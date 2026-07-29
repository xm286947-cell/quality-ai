from __future__ import annotations

import pytest

from business_agent.contracts import (
    CONTRACT_VERSION,
    ErrorDetail,
    EvidenceReference,
    ExecutionRequest,
    ExecutionResult,
    ExecutionStatus,
    KnowledgeItemContract,
    KnowledgeQuery,
    KnowledgeRequestContract,
    KnowledgeResponseContract,
    TraceContext,
)
from business_agent.validators import ContractValidationError, ContractValidator


def test_execution_request_serialization_round_trip():
    request = ExecutionRequest(
        request_id="REQ-P01-001",
        agent_id="repeat_case",
        inputs={"input": "sample.xlsx"},
        options={"top_k": 5},
    )
    payload = request.model_dump(mode="json")
    restored = ContractValidator.validate(ExecutionRequest, payload)
    assert restored == request
    assert payload["contract_version"] == CONTRACT_VERSION


def test_failed_execution_requires_error():
    with pytest.raises(ValueError):
        ExecutionResult(
            request_id="REQ-P01-002",
            agent_id="repeat_case",
            status=ExecutionStatus.FAILED,
        )
    result = ExecutionResult(
        request_id="REQ-P01-002",
        agent_id="repeat_case",
        status=ExecutionStatus.FAILED,
        error=ErrorDetail(code="AGENT_EXECUTION_FAILED", message="failed"),
    )
    assert result.error and result.error.code == "AGENT_EXECUTION_FAILED"


def test_knowledge_contract_carries_evidence_and_trace():
    request = KnowledgeRequestContract(
        request_id="REQ-P01-003",
        service_id="repeat_case_service",
        query=KnowledgeQuery(text="CAN接收拥堵导致重启"),
    )
    response = KnowledgeResponseContract(
        request_id=request.request_id,
        service_id=request.service_id,
        status=ExecutionStatus.SUCCESS,
        items=[KnowledgeItemContract(
            knowledge_id="CASE-001",
            score=0.91,
            evidence=[EvidenceReference(evidence_id="E-001", source_id="CASE-001")],
        )],
        total=1,
        trace=TraceContext(trace_id="TRACE-001", request_id=request.request_id),
    )
    payload = response.model_dump(mode="json")
    assert payload["items"][0]["evidence"][0]["evidence_id"] == "E-001"
    assert payload["trace"]["trace_id"] == "TRACE-001"


def test_validator_rejects_unsupported_version():
    payload = {
        "contract_version": "V9.9",
        "request_id": "REQ-P01-004",
        "agent_id": "repeat_case",
        "inputs": {},
        "options": {},
    }
    with pytest.raises(ContractValidationError) as exc_info:
        ContractValidator.validate(ExecutionRequest, payload)
    assert exc_info.value.code == "UNSUPPORTED_CONTRACT_VERSION"


def test_contract_models_forbid_unknown_fields():
    payload = {
        "contract_version": CONTRACT_VERSION,
        "request_id": "REQ-P01-005",
        "agent_id": "repeat_case",
        "inputs": {},
        "options": {},
        "unknown": True,
    }
    with pytest.raises(ContractValidationError) as exc_info:
        ContractValidator.validate(ExecutionRequest, payload)
    assert exc_info.value.code == "CONTRACT_VALIDATION_FAILED"
