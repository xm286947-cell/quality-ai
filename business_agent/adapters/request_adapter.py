from __future__ import annotations

from business_agent.contracts.execution import ExecutionRequest
from business_agent.models import RuntimeRequest


class RequestAdapter:
    """
    Convert external execution contract
    into runtime internal request model.
    """

    @staticmethod
    def to_runtime(request: ExecutionRequest) -> RuntimeRequest:
        return RuntimeRequest(
            agent_id=request.agent_id,
            request_id=request.request_id,
            inputs=request.inputs,
            options=request.options,
        )
