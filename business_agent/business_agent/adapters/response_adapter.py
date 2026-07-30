from __future__ import annotations

from business_agent.contracts.common import ExecutionStatus
from business_agent.contracts.execution import ExecutionResult
from business_agent.models import RuntimeResult

from .trace_adapter import TraceAdapter


class ResponseAdapter:
    """Convert the internal runtime result into the public execution result."""

    @staticmethod
    def from_runtime(result: RuntimeResult) -> ExecutionResult:
        try:
            status = ExecutionStatus(str(result.status).upper())
        except ValueError:
            status = ExecutionStatus.FAILED

        return ExecutionResult(
            request_id=result.request_id,
            agent_id=result.agent_id,
            agent_version=result.agent_version,
            status=status,
            output=dict(result.output),
            trace=TraceAdapter.from_path(
                result.trace_path,
                request_id=result.request_id,
            ),
            trace_path=result.trace_path,
        )
