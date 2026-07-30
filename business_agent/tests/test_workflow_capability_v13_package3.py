from __future__ import annotations

import unittest

from business_agent.capability.models import CapabilityResult
from business_agent.models import AgentProfile, RuntimeContext, RuntimeRequest, WorkflowNode
from business_agent.workflow import (
    CapabilityNodeConfigurationError,
    HandlerRegistry,
    NodeStatus,
    WorkflowEngine,
    capability_result_to_node_result,
    register_capability_handlers,
)


class FakeRuntimeBinding:
    def __init__(self, result: CapabilityResult) -> None:
        self.result = result
        self.calls = []

    def invoke(self, context, capability_type, binding_name, payload=None):
        self.calls.append((capability_type, binding_name, payload))
        context.data.setdefault("capabilities", {}).setdefault(capability_type, {})[
            "last_status"
        ] = self.result.status
        return self.result


def make_result(status: str) -> CapabilityResult:
    return CapabilityResult(
        capability_type="knowledge",
        binding_name="repeat_case.search",
        operation="query",
        status=status,
        request_id="REQ-1",
        response_id="RESP-1",
        trace_id="TRACE-1",
        items=[{"id": "K-1"}] if status != "no_result" else [],
        evidence=[{"source": "case-1"}] if status != "no_result" else [],
        warnings=[{"code": "DEGRADED"}] if status == "partial_success" else [],
        errors=[{"message": "provider failed", "retryable": False}]
        if status == "failed"
        else [],
        metadata={"provider": "fake"},
        degraded=status == "partial_success",
    )


def make_context(node: WorkflowNode) -> RuntimeContext:
    return RuntimeContext(
        request=RuntimeRequest(
            agent_id="repeat_case",
            request_id="REQ-1",
            inputs={"query": "motor alarm"},
        ),
        profile=AgentProfile(
            agent_id="repeat_case",
            name="Repeat Case",
            version="1.0",
            description="",
            workflow=(node,),
        ),
        data={"identity": {"trace_id": "TRACE-1"}},
    )


class CapabilityResultMappingTests(unittest.TestCase):
    def test_all_contract_statuses_are_mapped(self):
        node = WorkflowNode("n1", "capability", "capability.invoke")
        expected = {
            "success": NodeStatus.SUCCESS,
            "partial_success": NodeStatus.PARTIAL_SUCCESS,
            "no_result": NodeStatus.NO_RESULT,
            "failed": NodeStatus.FAILED,
        }
        for status, node_status in expected.items():
            with self.subTest(status=status):
                result = capability_result_to_node_result(node, make_result(status))
                self.assertEqual(node_status, result.status)

    def test_failed_result_contains_error(self):
        node = WorkflowNode("n1", "capability", "capability.invoke")
        result = capability_result_to_node_result(node, make_result("failed"))
        self.assertEqual("CapabilityFailed", result.error["type"])


class CapabilityWorkflowTests(unittest.TestCase):
    def test_success_end_to_end(self):
        node = WorkflowNode(
            id="knowledge_query",
            type="capability",
            handler="capability.invoke",
            config={
                "capability_type": "knowledge",
                "binding_name": "repeat_case.search",
                "payload": {"filters": {"product": "PLC"}},
            },
        )
        runtime = FakeRuntimeBinding(make_result("success"))
        registry = register_capability_handlers(HandlerRegistry(), runtime)
        context = make_context(node)

        output = WorkflowEngine(registry).execute(context)

        self.assertEqual("success", context.node_results[node.id]["status"])
        self.assertEqual("K-1", output["items"][0]["id"])
        self.assertEqual("motor alarm", runtime.calls[0][2]["inputs"]["query"])
        self.assertIn("last_capability_result", context.data)
        self.assertEqual("success", context.data["capabilities"]["knowledge"]["last_status"])

    def test_partial_success_respects_node_policy(self):
        node = WorkflowNode(
            id="knowledge_query",
            type="capability",
            handler="capability.invoke",
            config={"capability_type": "knowledge", "binding_name": "search"},
            runtime_policy={"allow_partial_success": True},
        )
        runtime = FakeRuntimeBinding(make_result("partial_success"))
        context = make_context(node)
        WorkflowEngine(register_capability_handlers(HandlerRegistry(), runtime)).execute(context)
        self.assertEqual("partial_success", context.node_results[node.id]["status"])

    def test_no_result_is_first_class_status(self):
        node = WorkflowNode(
            id="knowledge_query",
            type="capability",
            handler="capability.invoke",
            config={"capability_type": "knowledge", "binding_name": "search"},
        )
        runtime = FakeRuntimeBinding(make_result("no_result"))
        context = make_context(node)
        WorkflowEngine(register_capability_handlers(HandlerRegistry(), runtime)).execute(context)
        self.assertEqual("no_result", context.node_results[node.id]["status"])

    def test_failed_can_continue(self):
        node = WorkflowNode(
            id="knowledge_query",
            type="capability",
            handler="capability.invoke",
            config={"capability_type": "knowledge", "binding_name": "search"},
            runtime_policy={"on_failure": "continue"},
        )
        runtime = FakeRuntimeBinding(make_result("failed"))
        context = make_context(node)
        WorkflowEngine(register_capability_handlers(HandlerRegistry(), runtime)).execute(context)
        self.assertEqual("failed", context.node_results[node.id]["status"])

    def test_missing_binding_name_fails_validation(self):
        node = WorkflowNode(
            id="bad",
            type="capability",
            handler="capability.invoke",
            config={"capability_type": "knowledge"},
        )
        runtime = FakeRuntimeBinding(make_result("success"))
        registry = register_capability_handlers(HandlerRegistry(), runtime)
        with self.assertRaises(CapabilityNodeConfigurationError):
            registry.resolve("capability.invoke")(make_context(node), node)

    def test_include_context_is_opt_in(self):
        node = WorkflowNode(
            id="knowledge_query",
            type="capability",
            handler="capability.invoke",
            config={
                "capability_type": "knowledge",
                "binding_name": "search",
                "include_context": True,
            },
        )
        runtime = FakeRuntimeBinding(make_result("success"))
        context = make_context(node)
        WorkflowEngine(register_capability_handlers(HandlerRegistry(), runtime)).execute(context)
        self.assertEqual("TRACE-1", runtime.calls[0][2]["context"]["identity"]["trace_id"])


if __name__ == "__main__":
    unittest.main()
