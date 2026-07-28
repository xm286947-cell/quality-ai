from __future__ import annotations

from knowledge_capability.adapters import BusinessAgentAdapter
from knowledge_capability.contracts import KnowledgeResponse
from knowledge_capability.framework.runtime import KnowledgeCapabilityRuntime
from knowledge_capability.registry import ServiceRegistration, ServiceRegistry


class _Profile:
    service_id = "repeat_case_service"
    status = "active"
    version = "1.0"


class _Loader:
    def load(self, name):
        return _Profile()


class _Handler:
    def handle(self, request):
        return KnowledgeResponse(
            request_id=request.request_id,
            service_id=request.service_id,
            result={"results": [], "query": request.query},
        )


def test_business_agent_to_runtime_e2e():
    registry = ServiceRegistry()
    registry.register(
        ServiceRegistration(
            service_id="repeat_case_service",
            version="1.0",
            status="active",
            profile_name="repeat_case_service",
            handler=_Handler(),
        )
    )
    runtime = KnowledgeCapabilityRuntime(registry, _Loader())
    response = BusinessAgentAdapter(runtime).query(
        {
            "contract_version": "V1.0",
            "service_id": "repeat_case_service",
            "query": {"text": "软件运行偶发崩溃"},
            "options": {"top_k": 5},
            "caller": {"type": "business_agent", "agent_id": "repeat_case_agent"},
        }
    )
    assert response["success"] is True
    stages = [item["stage"] for item in response["trace"]]
    assert "contract_validation" in stages
    assert "service_execute" in stages
    assert "result_mapping" in stages
