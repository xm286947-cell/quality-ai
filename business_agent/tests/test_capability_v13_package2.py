from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from business_agent.capability import (
    CapabilityBinding,
    CapabilityNotFoundError,
    CapabilityRegistry,
    CapabilityValidationError,
    DependencyContainer,
    ServiceLocator,
)
from business_agent.capability.errors import CapabilityInvocationError
from business_agent.capability.knowledge import KnowledgeGateway
from business_agent.capability.runtime_binding import RuntimeCapabilityBinding


@dataclass
class Request:
    agent_id: str = "repeat_case"
    request_id: str = "REQ-001"
    inputs: dict[str, Any] = field(default_factory=lambda: {"text": "motor alarm"})


@dataclass
class Profile:
    agent_id: str = "repeat_case"
    version: str = "2.4"
    capability_bindings: dict[str, Any] = field(default_factory=lambda: {
        "knowledge": {
            "repeat_case": {
                "service_id": "repeat_case_service",
                "service_version": "1.0",
                "schema_version": "1.0",
                "operation": "query_knowledge",
                "requested_fields": ["title", "root_cause"],
                "default_options": {"top_k": 10},
                "runtime_policy": {
                    "timeout_ms": 1000,
                    "retry": {"max_attempts": 2, "backoff_ms": 0},
                },
            }
        }
    })


@dataclass
class Context:
    request: Request = field(default_factory=Request)
    profile: Profile = field(default_factory=Profile)
    data: dict[str, Any] = field(default_factory=lambda: {
        "identity": {"trace_id": "TRACE-001", "execution_id": "EXEC-001"}
    })


class FakeClient:
    def __init__(self, response: dict[str, Any], fail_times: int = 0) -> None:
        self.response = response
        self.fail_times = fail_times
        self.calls: list[tuple[str, dict[str, Any], int]] = []

    def invoke(self, operation, request, *, timeout_ms):
        self.calls.append((operation, request, timeout_ms))
        if self.fail_times:
            self.fail_times -= 1
            raise CapabilityInvocationError("temporary timeout", retryable=True)
        return self.response


SUCCESS_RESPONSE = {
    "contract_version": "1.0",
    "request_id": "REQ-001",
    "response_id": "RESP-001",
    "knowledge_trace_id": "KTRACE-001",
    "status": "success",
    "result": {
        "items": [{
            "knowledge_id": "K-001",
            "knowledge_version": "1.0",
            "knowledge_type": "case",
            "rank": 1,
            "title": "Known motor alarm",
            "summary": "Repeated connector issue",
            "score": 0.82,
            "fields": {"root_cause": "connector"},
            "evidence_refs": ["EV-001"],
        }],
        "evidence": [{"evidence_id": "EV-001", "source": "case-db"}],
    },
    "warnings": [],
    "errors": [],
}


class CapabilityBindingTests(unittest.TestCase):
    def test_parse_binding(self):
        locator = ServiceLocator()
        bindings = locator.load_profile_bindings(Profile())
        binding = locator.resolve(bindings, "knowledge", "repeat_case")
        self.assertEqual(binding.service_id, "repeat_case_service")
        self.assertEqual(binding.runtime_policy.max_attempts, 2)

    def test_missing_required_binding_field(self):
        with self.assertRaises(CapabilityValidationError):
            CapabilityBinding.from_dict("x", "knowledge", {"operation": "query_knowledge"})

    def test_missing_binding(self):
        with self.assertRaises(CapabilityNotFoundError):
            ServiceLocator().resolve({}, "knowledge", "missing")


class RegistryAndContainerTests(unittest.TestCase):
    def test_registry(self):
        registry = CapabilityRegistry()
        registry.register("knowledge", lambda: "gateway")
        self.assertEqual(registry.resolve("knowledge")(), "gateway")
        self.assertTrue(registry.contains("knowledge"))

    def test_container(self):
        container = DependencyContainer()
        container.register_instance("value", 3)
        container.register_factory("double", lambda c: c.resolve("value") * 2)
        self.assertEqual(container.resolve("double"), 6)


class KnowledgeGatewayTests(unittest.TestCase):
    def test_request_mapping_and_response_normalization(self):
        context = Context()
        binding = ServiceLocator().resolve(
            ServiceLocator().load_profile_bindings(context.profile),
            "knowledge",
            "repeat_case",
        )
        client = FakeClient(SUCCESS_RESPONSE)
        result = KnowledgeGateway(client).invoke(binding, context=context)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.items[0]["knowledge_id"], "K-001")
        sent = client.calls[0][1]
        self.assertEqual(sent["contract_version"], "1.0")
        self.assertEqual(sent["caller"]["agent_id"], "repeat_case")
        self.assertEqual(sent["service"]["schema_version"], "1.0")
        self.assertEqual(context.data["capabilities"]["knowledge"]["last_status"], "success")
        self.assertEqual(len(context.data["capabilities"]["knowledge"]["evidence"]), 1)

    def test_retry_on_retryable_failure(self):
        context = Context()
        binding = ServiceLocator().resolve(
            ServiceLocator().load_profile_bindings(context.profile),
            "knowledge",
            "repeat_case",
        )
        client = FakeClient(SUCCESS_RESPONSE, fail_times=1)
        result = KnowledgeGateway(client).invoke(binding, context=context)
        self.assertEqual(result.status, "success")
        self.assertEqual(len(client.calls), 2)

    def test_partial_success_is_degraded(self):
        response = dict(SUCCESS_RESPONSE)
        response["status"] = "partial_success"
        response["warnings"] = [{"code": "PARTIAL", "message": "limited data"}]
        context = Context()
        binding = ServiceLocator().resolve(
            ServiceLocator().load_profile_bindings(context.profile),
            "knowledge",
            "repeat_case",
        )
        result = KnowledgeGateway(FakeClient(response)).invoke(binding, context=context)
        self.assertTrue(result.degraded)
        self.assertEqual(
            context.data["capabilities"]["knowledge"]["warnings"][0]["code"],
            "PARTIAL",
        )

    def test_no_result_is_not_failure(self):
        response = {
            "contract_version": "1.0",
            "status": "no_result",
            "request_id": "REQ-001",
            "result": {"items": [], "evidence": []},
        }
        context = Context()
        binding = ServiceLocator().resolve(
            ServiceLocator().load_profile_bindings(context.profile),
            "knowledge",
            "repeat_case",
        )
        result = KnowledgeGateway(FakeClient(response)).invoke(binding, context=context)
        self.assertTrue(result.successful)
        self.assertEqual(result.items, [])

    def test_invalid_score_is_rejected(self):
        response = dict(SUCCESS_RESPONSE)
        response["result"] = {
            "items": [dict(SUCCESS_RESPONSE["result"]["items"][0], score=1.5)]
        }
        context = Context()
        binding = ServiceLocator().resolve(
            ServiceLocator().load_profile_bindings(context.profile),
            "knowledge",
            "repeat_case",
        )
        with self.assertRaises(CapabilityValidationError):
            KnowledgeGateway(FakeClient(response)).invoke(binding, context=context)


class RuntimeBindingTests(unittest.TestCase):
    def test_runtime_binding_end_to_end(self):
        client = FakeClient(SUCCESS_RESPONSE)
        integration = RuntimeCapabilityBinding.create_default(knowledge_client=client)
        context = Context()
        integration.attach(context)
        result = integration.invoke(
            context,
            "knowledge",
            "repeat_case",
            {"query": {"text": "motor alarm"}},
        )
        self.assertEqual(result.response_id, "RESP-001")
        self.assertEqual(
            context.data["capabilities"]["knowledge"]["items"][0]["title"],
            "Known motor alarm",
        )


if __name__ == "__main__":
    unittest.main()
