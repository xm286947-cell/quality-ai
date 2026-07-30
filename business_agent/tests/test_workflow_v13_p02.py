from __future__ import annotations

import unittest

from business_agent.models import (
    AgentProfile,
    RuntimeContext,
    RuntimeRequest,
    WorkflowNode,
)
from business_agent.workflow import (
    HandlerRegistry,
    NodeResult,
    NodeStatus,
    WorkflowEngine,
    WorkflowExecutionError,
)


class WorkflowV13P02Test(unittest.TestCase):
    def build_context(self, nodes: tuple[WorkflowNode, ...]) -> RuntimeContext:
        profile = AgentProfile(
            agent_id="test_agent",
            name="Test Agent",
            version="1.0",
            description="test",
            workflow=nodes,
        )
        request = RuntimeRequest(agent_id="test_agent", inputs={"value": 1})
        return RuntimeContext(request=request, profile=profile, data={})

    def test_node_result_and_context_merge(self) -> None:
        registry = HandlerRegistry()
        registry.register(
            "input.parse",
            lambda context, node: NodeResult(
                node_id=node.id,
                status=NodeStatus.SUCCESS,
                output={"parsed": True},
                context_updates={"parsed_value": 2},
            ),
        )
        context = self.build_context(
            (WorkflowNode(id="parse", type="input.parse", handler="input.parse"),)
        )

        output = WorkflowEngine(registry).execute(context)

        self.assertEqual(output, {"parsed": True})
        self.assertEqual(context.data["parsed_value"], 2)
        self.assertEqual(context.node_results["parse"]["status"], "success")

    def test_disabled_node_is_skipped(self) -> None:
        registry = HandlerRegistry()
        context = self.build_context(
            (
                WorkflowNode(
                    id="disabled",
                    type="business.test",
                    handler="not.registered",
                    enabled=False,
                ),
            )
        )

        output = WorkflowEngine(registry).execute(context)

        self.assertEqual(
            context.node_results["disabled"]["status"],
            "skipped",
        )
        self.assertIn("node_results", output)

    def test_failure_stops_by_default(self) -> None:
        registry = HandlerRegistry()
        registry.register(
            "failed",
            lambda context, node: (_ for _ in ()).throw(ValueError("boom")),
        )
        context = self.build_context(
            (WorkflowNode(id="failed", type="business.test", handler="failed"),)
        )

        with self.assertRaises(WorkflowExecutionError):
            WorkflowEngine(registry).execute(context)

        self.assertEqual(context.node_results["failed"]["status"], "failed")

    def test_failure_continue_policy(self) -> None:
        registry = HandlerRegistry()

        def failed(context, node):
            raise ValueError("boom")

        registry.register("failed", failed)
        registry.register(
            "next",
            lambda context, node: {
                "status": "success",
                "output": {"completed": True},
            },
        )
        context = self.build_context(
            (
                WorkflowNode(
                    id="failed",
                    type="business.test",
                    handler="failed",
                    runtime_policy={"on_failure": "continue"},
                ),
                WorkflowNode(
                    id="next",
                    type="result.build",
                    handler="next",
                ),
            )
        )

        output = WorkflowEngine(registry).execute(context)

        self.assertEqual(output, {"completed": True})
        self.assertEqual(context.node_results["failed"]["status"], "failed")
        self.assertEqual(context.node_results["next"]["status"], "success")

    def test_duplicate_handler_requires_explicit_overwrite(self) -> None:
        registry = HandlerRegistry()
        registry.register("x", lambda context, node: None)
        with self.assertRaises(ValueError):
            registry.register("x", lambda context, node: None)


if __name__ == "__main__":
    unittest.main()
