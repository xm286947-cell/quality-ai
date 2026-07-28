from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from business_agent.contracts.execution import (
    ExecutionArtifact,
    ExecutionContext,
    ExecutionError,
    ExecutionResponse,
    ExecutionTrace,
)


class ExecutionResultBuilder:
    @staticmethod
    def _artifacts_from_context(context: ExecutionContext) -> list[ExecutionArtifact]:
        raw_items = context.variables.get("artifacts", [])
        artifacts: list[ExecutionArtifact] = []
        for item in raw_items if isinstance(raw_items, list) else []:
            try:
                artifacts.append(item if isinstance(item, ExecutionArtifact) else ExecutionArtifact.model_validate(item))
            except ValidationError:
                continue
        return artifacts

    @staticmethod
    def _warnings_from_context(context: ExecutionContext) -> list[str]:
        raw_items: Any = context.variables.get("warnings", [])
        if not isinstance(raw_items, list):
            return []
        return [str(item) for item in raw_items if str(item).strip()]

    @classmethod
    def success(
        cls,
        context: ExecutionContext,
        trace: list[ExecutionTrace],
        artifacts: list[ExecutionArtifact] | None = None,
        warnings: list[str] | None = None,
    ) -> ExecutionResponse:
        resolved_warnings = warnings if warnings is not None else cls._warnings_from_context(context)
        resolved_artifacts = artifacts if artifacts is not None else cls._artifacts_from_context(context)
        status = "partial_success" if resolved_warnings else "success"
        return ExecutionResponse(
            request_id=context.request_id,
            trace_id=context.trace_id,
            agent_id=context.agent_id,
            status=status,
            result=context.result,
            artifacts=resolved_artifacts,
            trace=trace,
            warnings=resolved_warnings,
        )

    @staticmethod
    def failed(
        context: ExecutionContext,
        trace: list[ExecutionTrace],
        error: ExecutionError,
    ) -> ExecutionResponse:
        return ExecutionResponse(
            request_id=context.request_id,
            trace_id=context.trace_id,
            agent_id=context.agent_id,
            status="failed",
            result={},
            trace=trace,
            error=error,
        )
