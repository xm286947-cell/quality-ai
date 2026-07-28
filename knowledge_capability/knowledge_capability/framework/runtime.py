from __future__ import annotations

from knowledge_capability.contracts import KnowledgeRequest, KnowledgeResponse
from knowledge_capability.profiles import ServiceProfileLoader
from knowledge_capability.registry import ServiceRegistry
from knowledge_capability.runtime.context import RuntimeContext
from knowledge_capability.runtime.result_mapper import ResultMapper
from knowledge_capability.runtime.trace import TraceManager


class KnowledgeCapabilityRuntime:
    """Unified runtime for contract validation, service resolution and execution."""

    def __init__(self, registry: ServiceRegistry, profile_loader: ServiceProfileLoader) -> None:
        self.registry = registry
        self.profile_loader = profile_loader

    def execute(self, request: KnowledgeRequest) -> KnowledgeResponse:
        context = RuntimeContext(request=request, runtime_options=dict(request.options))
        trace = TraceManager()
        try:
            with trace.step("contract_validation", "KnowledgeRequest"):
                request.validate()
            with trace.step("service_resolution", "ServiceRegistry"):
                context.registration = self.registry.get(request.service_id)
            with trace.step("profile_resolution", "ServiceProfileLoader"):
                context.profile = self.profile_loader.load(context.registration.profile_name)
                if context.profile.service_id != context.registration.service_id:
                    raise ValueError(f"Profile service_id不匹配: {context.profile.service_id} != {context.registration.service_id}")
                if context.registration.status != "active" or context.profile.status != "active":
                    raise RuntimeError(f"服务不可用: {request.service_id}")
            with trace.step("service_execute", type(context.registration.handler).__name__):
                response = context.registration.handler.handle(request)
            with trace.step("result_mapping", "ResultMapper"):
                mapped = response
            return ResultMapper.success(mapped, trace.entries)
        except Exception as exc:
            trace.record("runtime_error", "KnowledgeCapabilityRuntime", "failed", {"error_type": type(exc).__name__})
            return ResultMapper.failure(request, trace.entries, exc)

    def query(self, request: KnowledgeRequest) -> KnowledgeResponse:
        return self.execute(request)
