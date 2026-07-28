from __future__ import annotations

from pathlib import Path

import pytest

from business_agent.knowledge.adapter import KnowledgeContractAdapter
from business_agent.knowledge.client import KnowledgeClient
from business_agent.knowledge.errors import KnowledgeConfigurationError
from business_agent.knowledge.models import KnowledgeRequest
from business_agent.models import AgentProfile, RuntimeContext, RuntimeRequest, WorkflowNode

ROOT = Path(__file__).resolve().parents[1]


def test_mock_contract_response_parses() -> None:
    client = KnowledgeClient(ROOT, {"provider": "mock", "fixture": "tests/contract/mock_knowledge_response.json"})
    response = client.search(KnowledgeRequest("TEST-KNOWLEDGE-001", "repeat_case_service", {"text": "CAN拥堵"}, options={"top_k": 5}))
    assert response.status == "SUCCESS"
    assert response.total == 1
    assert response.items[0].knowledge_id == "CASE-001"
    assert response.items[0].evidence[0].evidence_id == "EV-001"


def test_capability_provider_requires_base_url() -> None:
    client = KnowledgeClient(ROOT, {"provider": "capability", "base_url": ""})
    with pytest.raises(KnowledgeConfigurationError):
        client.search(KnowledgeRequest("REQ-1", "repeat_case_service", {"text": "query"}))


def test_adapter_writes_contract_context() -> None:
    profile = AgentProfile("repeat_case", "REPEAT_CASE", "test", "", ())
    request = RuntimeRequest(
        "repeat_case",
        {"problem_description": "CAN接收拥堵", "top_k": 3},
        request_id="TEST-KNOWLEDGE-001",
        options={"knowledge": {"provider": "mock", "fixture": "tests/contract/mock_knowledge_response.json"}},
    )
    context = RuntimeContext(request, profile, data={"cases": [{"case_id": "CASE001", "query_text": "CAN接收拥堵"}]})
    node = WorkflowNode("knowledge_search", "python_handler", "knowledge.search", config={"service_id": "repeat_case_service"})
    result = KnowledgeContractAdapter(ROOT).search(context, node)
    assert result["summary"]["recall_count"] == 1
    assert result["summary"]["evidence_count"] == 1
    assert result["context_updates"]["knowledge_request"]["contract_version"] == "V1.0"


def test_adapter_builds_frozen_v1_request_shape() -> None:
    profile = AgentProfile("repeat_case", "REPEAT_CASE", "test", "", ())
    request = RuntimeRequest(
        "repeat_case",
        {"problem_description": "CAN接收拥堵", "top_k": 3},
        request_id="REQ-CONTRACT-SHAPE",
        options={"knowledge": {"provider": "mock", "fixture": "tests/contract/mock_knowledge_response.json"}},
    )
    context = RuntimeContext(request, profile, data={"cases": [{"case_id": "CASE001", "query_text": "CAN接收拥堵"}]})
    node = WorkflowNode(
        "knowledge_search",
        "python_handler",
        "knowledge.search",
        config={"service_id": "repeat_case_service"},
    )
    payload = KnowledgeContractAdapter(ROOT).search(context, node)["context_updates"]["knowledge_request"]
    assert payload["query"] == {"text": "CAN接收拥堵"}
    assert payload["options"]["top_k"] == 3
    assert payload["caller"]["type"] == "business_agent"
    assert payload["service_id"] == "repeat_case_service"
    assert payload["contract_version"] == "V1.0"
