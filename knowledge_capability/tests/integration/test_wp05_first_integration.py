from __future__ import annotations
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

from business_agent.api import create_app
from business_agent.handlers import ContextHandler, KnowledgeHandler, LLMHandler, PromptHandler, ResultHandler
from business_agent.knowledge import KnowledgeHttpClient, KnowledgeHttpConfig
from business_agent.runtime import AgentDefinition, AgentRegistry, ExecutionRuntime
from knowledge_capability.api import create_app as create_knowledge_app
from prepare_i10_fixture import prepare


def _runtime_with_http_bridge(project_root) -> ExecutionRuntime:
    prepare(project_root)
    knowledge_app = create_knowledge_app(project_root)
    knowledge_test_client = TestClient(knowledge_app)

    def route(request: httpx.Request) -> httpx.Response:
        response = knowledge_test_client.post(request.url.path, content=request.content, headers={"content-type": "application/json"})
        return httpx.Response(response.status_code, json=response.json())

    config = KnowledgeHttpConfig(base_url="http://knowledge.test", max_retries=0)
    client = KnowledgeHttpClient(config, transport=httpx.MockTransport(route))
    registry = AgentRegistry()
    registry.register(AgentDefinition.create("repeat_case_agent", [
        ContextHandler(), KnowledgeHandler(client), PromptHandler(), LLMHandler(), ResultHandler()
    ]))
    return ExecutionRuntime(registry=registry)


def test_client_to_repeat_case_full_chain():
    project_root = Path(__file__).resolve().parents[2]
    app = create_app(_runtime_with_http_bridge(project_root))
    client = TestClient(app)
    response = client.post("/v1/executions", json={
        "contract_version": "V1.1",
        "request_id": "wp05-e2e-001",
        "agent_id": "repeat_case_agent",
        "input": {"text": "CAN接收拥堵导致软件保护重启"},
        "options": {"knowledge": {"service_id": "repeat_case_service", "top_k": 3}},
    })
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"success", "partial_success"}
    assert body["request_id"] == "wp05-e2e-001"
    assert body["result"]["accepted"] is True
    assert body["result"]["knowledge"]["status"] == "success"
    assert body["result"]["analysis"]
    assert [item["step"] for item in body["trace"]] == ["context", "knowledge", "prompt", "llm", "result"]


def test_execution_contract_stops_at_business_agent_boundary():
    project_root = Path(__file__).resolve().parents[2]
    app = create_app(_runtime_with_http_bridge(project_root))
    response = TestClient(app).post("/v1/executions", json={
        "contract_version": "V1.1",
        "agent_id": "repeat_case_agent",
        "input": {"text": "test"},
        "service_id": "repeat_case_service",
    })
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "EXECUTION_REQUEST_INVALID"


def test_business_agent_health():
    project_root = Path(__file__).resolve().parents[2]
    response = TestClient(create_app(_runtime_with_http_bridge(project_root))).get("/health")
    assert response.status_code == 200
    assert response.json()["contract_version"] == "V1.1"
