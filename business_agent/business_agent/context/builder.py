from __future__ import annotations

from business_agent.models import AgentProfile, RuntimeContext, RuntimeRequest


class ContextBuilder:
    """Build the platform-owned runtime context for every Agent."""

    def build(self, request: RuntimeRequest, profile: AgentProfile) -> RuntimeContext:
        return RuntimeContext(
            request=request,
            profile=profile,
            data={
                "inputs": dict(request.inputs),
                "options": dict(request.options),
                "runtime": {"agent_id": profile.agent_id, "agent_version": profile.version},
            },
        )
