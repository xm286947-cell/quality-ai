from __future__ import annotations

from business_agent.contracts.execution import ExecutionRequest
from business_agent.models import RuntimeRequest


class RequestAdapter:
    """Convert a public execution request into the internal runtime request."""

    @staticmethod
    def to_runtime(request: ExecutionRequest) -> RuntimeRequest:
        return RuntimeRequest(
            agent_id=request.agent_id,
            request_id=request.request_id,
            inputs=dict(request.inputs),
            options=dict(request.options),
        )
