from business_agent.contracts.execution import ExecutionArtifact, ExecutionContext
from business_agent.handlers import ExecutionHandler
from business_agent.runtime import AgentDefinition, AgentRegistry, ExecutionRuntime


class CompleteHandler(ExecutionHandler):
    name = "complete"

    def handle(self, context: ExecutionContext) -> ExecutionContext:
        context.result = {"done": True}
        context.variables["warnings"] = ["knowledge not configured"]
        context.variables["artifacts"] = [
            ExecutionArtifact(
                artifact_id="artifact-1",
                artifact_type="report",
                name="runtime-result",
                content={"done": True},
            )
        ]
        return context


class BrokenHandler(ExecutionHandler):
    name = "broken"

    def handle(self, context: ExecutionContext) -> ExecutionContext:
        raise RuntimeError("handler exploded")


def test_runtime_routes_registered_agent_and_collects_delivery_data():
    registry = AgentRegistry()
    registry.register(AgentDefinition.create("custom_agent", [CompleteHandler()]))
    response = ExecutionRuntime(registry=registry).execute(
        {"contract_version": "V1.1", "agent_id": "custom_agent", "input": {}}
    )
    assert response.status == "partial_success"
    assert response.result == {"done": True}
    assert response.warnings == ["knowledge not configured"]
    assert response.artifacts[0].artifact_id == "artifact-1"
    assert response.trace[0].step == "complete"


def test_runtime_returns_agent_not_found():
    response = ExecutionRuntime(registry=AgentRegistry()).execute(
        {"contract_version": "V1.1", "agent_id": "missing_agent", "input": {}}
    )
    assert response.status == "failed"
    assert response.error is not None
    assert response.error.code == "AGENT_NOT_FOUND"


def test_runtime_rejects_disabled_agent():
    registry = AgentRegistry()
    registry.register(AgentDefinition.create("disabled_agent", [CompleteHandler()], enabled=False))
    response = ExecutionRuntime(registry=registry).execute(
        {"contract_version": "V1.1", "agent_id": "disabled_agent", "input": {}}
    )
    assert response.error is not None
    assert response.error.code == "AGENT_DISABLED"


def test_runtime_preserves_failed_step_trace():
    registry = AgentRegistry()
    registry.register(AgentDefinition.create("broken_agent", [BrokenHandler()]))
    response = ExecutionRuntime(registry=registry).execute(
        {"contract_version": "V1.1", "agent_id": "broken_agent", "input": {}}
    )
    assert response.error is not None
    assert response.error.code == "EXECUTION_STEP_FAILED"
    assert response.error.details["failed_step"] == "broken"
    assert response.trace[0].status == "failed"


def test_runtime_rejects_unsupported_operation():
    response = ExecutionRuntime().execute(
        {
            "contract_version": "V1.1",
            "agent_id": "repeat_case_agent",
            "operation": "describe",
            "input": {},
        }
    )
    assert response.error is not None
    assert response.error.code == "EXECUTION_OPERATION_UNSUPPORTED"
