from __future__ import annotations

from pathlib import Path

from knowledge_capability.contracts import KnowledgeRequest, KnowledgeResponse
from knowledge_capability.framework.runtime import KnowledgeCapabilityRuntime
from knowledge_capability.registry import ServiceRegistration, ServiceRegistry
from knowledge_capability.runtime.context import RuntimeContext


class _Profile:
    service_id = "svc"
    status = "active"
    version = "1"


class _Loader:
    def load(self, name):
        assert name == "profile"
        return _Profile()


class _Handler:
    def handle(self, request):
        return KnowledgeResponse(request_id=request.request_id, service_id=request.service_id, result={"ok": True})


def _runtime():
    registry = ServiceRegistry()
    registry.register(ServiceRegistration(service_id="svc", version="1", status="active", profile_name="profile", handler=_Handler()))
    return KnowledgeCapabilityRuntime(registry, _Loader())


def test_runtime_context_exposes_request_identity():
    request = KnowledgeRequest(service_id="svc", query={"text": "x"})
    context = RuntimeContext(request=request)
    assert context.request_id == request.request_id
    assert context.service_id == "svc"


def test_runtime_execute_returns_mapped_response_and_trace():
    response = _runtime().execute(KnowledgeRequest(service_id="svc", query={"text": "x"}))
    assert response.success
    assert response.result == {"ok": True}
    stages = [entry.stage for entry in response.trace]
    assert stages[:4] == ["contract_validation", "service_resolution", "profile_resolution", "service_execute"]
    assert "result_mapping" in stages


def test_runtime_maps_missing_service_error():
    response = _runtime().execute(KnowledgeRequest(service_id="missing", query={}))
    assert not response.success
    assert response.error.code == "SERVICE_NOT_FOUND"
    assert response.trace[-1].stage == "runtime_error"

class _InactiveProfile:
    service_id = "svc"
    status = "disabled"
    version = "1"


class _InactiveLoader:
    def load(self, name):
        return _InactiveProfile()


def test_runtime_keeps_query_as_execute_compatibility_alias():
    request = KnowledgeRequest(service_id="svc", query={"text": "x"})
    query_response = _runtime().query(request)
    execute_response = _runtime().execute(request)
    assert query_response.success == execute_response.success
    assert query_response.result == execute_response.result
    assert [entry.stage for entry in query_response.trace] == [entry.stage for entry in execute_response.trace]


def test_runtime_rejects_inactive_profile_without_raising():
    registry = ServiceRegistry()
    registry.register(ServiceRegistration(service_id="svc", version="1", status="active", profile_name="profile", handler=_Handler()))
    response = KnowledgeCapabilityRuntime(registry, _InactiveLoader()).execute(
        KnowledgeRequest(service_id="svc", query={"text": "x"})
    )
    assert not response.success
    assert response.error.code == "SERVICE_EXECUTION_FAILED"
