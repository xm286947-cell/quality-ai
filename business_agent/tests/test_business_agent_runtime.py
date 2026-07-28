from __future__ import annotations

from pathlib import Path

import pytest

from business_agent.agent.profile_loader import AgentProfileLoader
from business_agent.models import RuntimeRequest
from business_agent.runtime.runtime import BusinessAgentRuntime


ROOT = Path(__file__).resolve().parents[1]


def test_repeat_case_profile_loads() -> None:
    profile = AgentProfileLoader(ROOT).load("repeat_case")
    assert profile.agent_id == "repeat_case"
    assert [node.handler for node in profile.workflow] == ["input.parse", "knowledge.search", "repeat_case.run_analysis"]


def test_runtime_lists_repeat_case() -> None:
    agents = BusinessAgentRuntime(ROOT).list_agents()
    assert any(item["agent_id"] == "repeat_case" for item in agents)


def test_runtime_executes_registered_handler(monkeypatch: pytest.MonkeyPatch) -> None:
    runtime = BusinessAgentRuntime(ROOT)

    def fake_handler(context, node):
        return {"summary": {"success": True}, "output": {"ok": True}}

    runtime.registry.register("input.parse", fake_handler)
    runtime.registry.register("knowledge.search", fake_handler)
    runtime.registry.register("repeat_case.run_analysis", fake_handler)
    result = runtime.run(RuntimeRequest(agent_id="repeat_case", inputs={}, request_id="TEST-RUNTIME-001"))
    assert result.status == "SUCCESS"
    assert result.output == {"ok": True}
    assert Path(result.trace_path).exists()
