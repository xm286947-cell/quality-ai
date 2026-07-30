from business_agent.adapters import RequestAdapter, ResponseAdapter, TraceAdapter
from business_agent.contracts.common import ExecutionStatus
from business_agent.contracts.execution import ExecutionRequest
from business_agent.models import RuntimeResult


def test_request_adapter():
    request = ExecutionRequest(
        request_id="REQ-1",
        agent_id="repeat_case",
        inputs={"input": "sample.xlsx"},
        options={"knowledge": {"provider": "mock"}},
    )
    runtime = RequestAdapter.to_runtime(request)
    assert runtime.request_id == "REQ-1"
    assert runtime.agent_id == "repeat_case"
    assert runtime.inputs["input"] == "sample.xlsx"


def test_response_adapter():
    runtime = RuntimeResult(
        request_id="REQ-1",
        agent_id="repeat_case",
        agent_version="1.0",
        status="SUCCESS",
        output={"ok": True},
        trace_path="output/trace.json",
    )
    result = ResponseAdapter.from_runtime(runtime)
    assert result.status == ExecutionStatus.SUCCESS
    assert result.trace.request_id == "REQ-1"
    assert result.trace.debug["trace_path"] == "output/trace.json"


def test_trace_adapter_empty_path():
    trace = TraceAdapter.from_path("", request_id="REQ-2")
    assert trace.request_id == "REQ-2"
    assert trace.debug == {}
