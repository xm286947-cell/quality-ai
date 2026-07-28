from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from business_agent.agent.profile_loader import AgentProfileLoader
from business_agent.context.builder import ContextBuilder
from business_agent.models import RuntimeRequest, RuntimeResult
from business_agent.plugin.loader import PluginLoader
from business_agent.result.engine import ResultEngine
from business_agent.trace.manager import TraceManager
from business_agent.workflow.engine import WorkflowEngine
from business_agent.workflow.handler_registry import HandlerRegistry


class BusinessAgentRuntime:
    """Business-neutral runtime: profiles and plugins provide all Agent behavior."""

    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root).resolve()
        self.loader = AgentProfileLoader(self.project_root)
        self.registry = HandlerRegistry()
        self.plugins = PluginLoader(self.project_root, self.registry)
        self.context_builder = ContextBuilder()
        self.result_engine = ResultEngine()

    def list_agents(self) -> list[dict[str, Any]]:
        return self.loader.list_profiles()

    def run(self, request: RuntimeRequest) -> RuntimeResult:
        request.request_id = request.request_id or f"RUN-{uuid.uuid4().hex[:12].upper()}"
        profile = self.loader.load(request.agent_id)
        self.plugins.load(profile.agent_id, profile.plugin)
        trace = TraceManager(self.project_root, request)
        context = self.context_builder.build(request, profile)
        try:
            raw_output = WorkflowEngine(self.registry, trace).execute(context)
            output = self.result_engine.normalize(raw_output, context.node_results)
            trace_path = trace.complete("SUCCESS")
            return RuntimeResult(request.request_id, profile.agent_id, profile.version, "SUCCESS", output, trace_path)
        except Exception as exc:
            trace.complete("FAILED", exc)
            raise
