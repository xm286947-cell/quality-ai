from __future__ import annotations

import httpx

from business_agent.handlers import ContextHandler, KnowledgeHandler, LLMHandler, PromptHandler, ResultHandler
from business_agent.knowledge import KnowledgeHttpClient, KnowledgeHttpConfig
from business_agent.runtime import ExecutionPipeline, ExecutionRuntime


def make_runtime(handler):
    config = KnowledgeHttpConfig(
        base_url="http://knowledge.test", query_path="/v1/knowledge/query",
        connect_timeout_seconds=0.1, read_timeout_seconds=0.1,
        max_retries=0, retry_backoff_seconds=0.0,
    )
    client = KnowledgeHttpClient(config, transport=httpx.MockTransport(handler))
    pipeline = ExecutionPipeline([
        ContextHandler(), KnowledgeHandler(client), PromptHandler(), LLMHandler(), ResultHandler()
    ])
    return ExecutionRuntime(pipeline)


def test_execution_runtime_consumes_knowledge_http_result():
    def handler(request: httpx.Request):
        payload = __import__("json").loads(request.content)
        assert payload["contract_version"] == "V1.0"
        assert payload["service_id"] == "repeat_case_service"
        assert payload["query"]["text"] == "CAN接收拥堵导致重启"
        return httpx.Response(200, json={
            "request_id": payload["request_id"], "service_id": payload["service_id"],
            "success": True, "result": {"results": [{"case_id": "CASE-CAN-001"}]},
            "evidence": [{"evidence_id": "ev-1"}], "trace": [], "warnings": [],
            "error": None, "contract_version": "V1.0", "created_at": "now",
        })

    response = make_runtime(handler).execute({
        "contract_version": "V1.1", "request_id": "req-e2e-1",
        "agent_id": "repeat_case_agent", "input": {"text": "CAN接收拥堵导致重启"},
        "options": {"knowledge": {"top_k": 3}},
    })
    assert response.status == "success"
    assert response.result["knowledge"]["result"]["results"][0]["case_id"] == "CASE-CAN-001"
    assert [item.step for item in response.trace] == ["context", "knowledge", "prompt", "llm", "result"]


def test_execution_runtime_maps_knowledge_unavailable():
    def handler(request: httpx.Request):
        raise httpx.ConnectError("offline", request=request)

    response = make_runtime(handler).execute({
        "contract_version": "V1.1", "request_id": "req-e2e-2",
        "agent_id": "repeat_case_agent", "input": {"text": "test"},
    })
    assert response.status == "failed"
    assert response.error.code == "KNOWLEDGE_SERVICE_UNAVAILABLE"
    assert response.error.retryable is True
    assert response.error.details["failed_step"] == "knowledge"


def test_knowledge_query_can_be_disabled():
    def unexpected(request: httpx.Request):
        raise AssertionError("HTTP must not be called")

    response = make_runtime(unexpected).execute({
        "contract_version": "V1.1", "request_id": "req-e2e-3",
        "agent_id": "repeat_case_agent", "input": {"text": "test"},
        "options": {"knowledge": {"enabled": False}},
    })
    assert response.status == "success"
    assert response.result["knowledge"]["status"] == "skipped"
