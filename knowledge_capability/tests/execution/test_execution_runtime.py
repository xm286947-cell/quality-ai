from business_agent.runtime import ExecutionRuntime


def test_runtime_execute_is_public_entry_point():
    response = ExecutionRuntime().execute(
        {
            "contract_version": "V1.1",
            "request_id": "req-wp01-001",
            "agent_id": "repeat_case_agent",
            "input": {"text": "CAN接收拥堵导致软件保护重启"},
            "options": {"knowledge": {"enabled": False}},
        }
    )
    assert response.status == "success"
    assert response.request_id == "req-wp01-001"
    assert response.result["accepted"] is True
    assert [item.step for item in response.trace] == ["context", "knowledge", "prompt", "llm", "result"]


def test_runtime_returns_contract_error_for_invalid_request():
    response = ExecutionRuntime().execute({"contract_version": "V1.1", "input": {}})
    assert response.status == "failed"
    assert response.error is not None
    assert response.error.code == "EXECUTION_REQUEST_INVALID"
