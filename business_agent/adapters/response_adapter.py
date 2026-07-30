from __future__ import annotations

from business_agent.contracts.execution import ExecutionResult
from business_agent.contracts.common import ExecutionStatus
from business_agent.models import RuntimeResult


class ResponseAdapter:
    """
    Convert runtime result into execution contract result.
    """

    @staticmethod
    def from_runtime(result: RuntimeResult) -> ExecutionResult:
        status = ExecutionStatus.SUCCESS

        if str(result.status).upper() == "FAILED":
            status = ExecutionStatus.FAILED

        return ExecutionResult(
            request_id=result.request_id,
            agent_id=result.agent_id,
            agent_version=result.agent_version,
            status=status,
            output=result.output,
            trace_path=result.trace_path,
        )
