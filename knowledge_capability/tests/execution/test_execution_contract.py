import pytest
from pydantic import ValidationError

from business_agent.contracts.execution import ExecutionRequest, ExecutionResponse


def test_execution_request_serialization_round_trip():
    request = ExecutionRequest(agent_id="repeat_case_agent", input={"text": "CAN拥堵"})
    restored = ExecutionRequest.model_validate_json(request.model_dump_json())
    assert restored.contract_version == "V1.1"
    assert restored.agent_id == "repeat_case_agent"
    assert restored.input["text"] == "CAN拥堵"


def test_execution_request_rejects_unsupported_contract_version():
    with pytest.raises(ValidationError):
        ExecutionRequest(contract_version="V1.0", agent_id="repeat_case_agent")


def test_execution_response_success_property():
    response = ExecutionResponse(
        request_id="req-1",
        trace_id="trace-1",
        agent_id="repeat_case_agent",
        status="success",
    )
    assert response.success is True
