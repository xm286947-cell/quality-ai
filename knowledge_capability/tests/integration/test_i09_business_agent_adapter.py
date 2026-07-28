from __future__ import annotations

from knowledge_capability.adapters import BusinessAgentAdapter
from knowledge_capability.contracts import Evidence, KnowledgeResponse, TraceEntry


class _Runtime:
    def execute(self, request):
        return KnowledgeResponse(
            request_id=request.request_id,
            service_id=request.service_id,
            result={"results": [{"case_id": "CASE-001", "score": 0.91}]},
            evidence=[Evidence("repeat-case:CASE-001", "repeat_case", "CASE-001")],
            trace=[TraceEntry("retrieve", "FakeRepository", "success")],
        )


def test_adapter_executes_runtime_and_maps_response():
    response = BusinessAgentAdapter(_Runtime()).execute(
        {
            "contract_version": "V1.0",
            "request_id": "req-001",
            "service_id": "repeat_case_service",
            "query": {"text": "软件崩溃"},
            "caller": {"type": "business_agent"},
        }
    )
    assert response["success"] is True
    assert response["contract_version"] == "V1.0"
    assert response["result"]["results"][0]["case_id"] == "CASE-001"
    assert response["evidence"][0]["source_ref"] == "CASE-001"


def test_adapter_maps_contract_error_without_calling_runtime():
    response = BusinessAgentAdapter(_Runtime()).execute(
        {"contract_version": "V2.0", "service_id": "repeat_case_service", "query": {}}
    )
    assert response["success"] is False
    assert response["error"]["code"] == "INVALID_REQUEST"
    assert response["contract_version"] == "V1.0"
