from __future__ import annotations

from uuid import uuid4

from pydantic import ValidationError

from business_agent.contracts.execution import ExecutionContext, ExecutionError, ExecutionRequest, ExecutionResponse

from .agent_registry import AgentRegistry
from .execution_pipeline import ExecutionPipeline, PipelineExecutionError
from .execution_result_builder import ExecutionResultBuilder


class ExecutionRuntime:
    """The only public Business Agent execution entry point."""

    def __init__(
        self,
        pipeline: ExecutionPipeline | None = None,
        *,
        registry: AgentRegistry | None = None,
    ) -> None:
        if pipeline is not None and registry is not None:
            raise ValueError("pipeline and registry are mutually exclusive")
        self._fixed_pipeline = pipeline
        self._registry = registry or (None if pipeline is not None else AgentRegistry.default())

    def execute(self, request: ExecutionRequest | dict) -> ExecutionResponse:
        execution_request, validation_failure = self._validate_request(request)
        if validation_failure is not None:
            return validation_failure
        assert execution_request is not None

        context = ExecutionContext(
            request_id=execution_request.request_id,
            trace_id=execution_request.trace_id or f"trace-{uuid4().hex}",
            agent_id=execution_request.agent_id,
            input=execution_request.input,
            variables={
                "client_context": execution_request.context,
                "options": execution_request.options,
                "caller": execution_request.caller,
                "operation": execution_request.operation,
                "execution_status": "accepted",
            },
        )

        if execution_request.operation != "execute":
            return ExecutionResultBuilder.failed(
                context,
                [],
                ExecutionError(
                    code="EXECUTION_OPERATION_UNSUPPORTED",
                    message=f"Unsupported execution operation: {execution_request.operation}",
                    details={"supported_operations": ["execute"]},
                ),
            )

        pipeline_or_error = self._resolve_pipeline(execution_request.agent_id, context)
        if isinstance(pipeline_or_error, ExecutionResponse):
            return pipeline_or_error

        context.variables["execution_status"] = "running"
        try:
            final_context, trace = pipeline_or_error.run(context)
            final_context.variables["execution_status"] = "completed"
            return ExecutionResultBuilder.success(final_context, trace)
        except PipelineExecutionError as exc:
            exc.context.variables["execution_status"] = "failed"
            details = {
                "failed_step": exc.failed_step,
                "error_type": type(exc.cause).__name__,
            }
            error_code = "EXECUTION_STEP_FAILED"
            retryable = False
            structured = getattr(exc.cause, "knowledge_error", None)
            if structured is not None:
                error_code = getattr(structured, "code", error_code)
                retryable = bool(getattr(structured, "retryable", False))
                details.update({
                    "knowledge_status_code": getattr(structured, "status_code", None),
                    "knowledge_details": getattr(structured, "details", {}),
                })
            return ExecutionResultBuilder.failed(
                exc.context,
                exc.trace,
                ExecutionError(
                    code=error_code,
                    message=str(exc),
                    retryable=retryable,
                    details=details,
                ),
            )
        except Exception as exc:
            context.variables["execution_status"] = "failed"
            return ExecutionResultBuilder.failed(
                context,
                [],
                ExecutionError(
                    code="EXECUTION_FAILED",
                    message=str(exc) or "Execution failed",
                    retryable=False,
                    details={"error_type": type(exc).__name__},
                ),
            )

    def _resolve_pipeline(
        self,
        agent_id: str,
        context: ExecutionContext,
    ) -> ExecutionPipeline | ExecutionResponse:
        if self._fixed_pipeline is not None:
            return self._fixed_pipeline
        assert self._registry is not None
        definition = self._registry.get(agent_id)
        if definition is None:
            return ExecutionResultBuilder.failed(
                context,
                [],
                ExecutionError(
                    code="AGENT_NOT_FOUND",
                    message=f"Business Agent is not registered: {agent_id}",
                    details={"agent_id": agent_id},
                ),
            )
        if not definition.enabled:
            return ExecutionResultBuilder.failed(
                context,
                [],
                ExecutionError(
                    code="AGENT_DISABLED",
                    message=f"Business Agent is disabled: {agent_id}",
                    details={"agent_id": agent_id},
                ),
            )
        return ExecutionPipeline(definition.handlers)

    @staticmethod
    def _validate_request(
        request: ExecutionRequest | dict,
    ) -> tuple[ExecutionRequest | None, ExecutionResponse | None]:
        try:
            parsed = request if isinstance(request, ExecutionRequest) else ExecutionRequest.model_validate(request)
            return parsed, None
        except ValidationError as exc:
            fallback = ExecutionContext(
                request_id=str(request.get("request_id", "invalid-request")) if isinstance(request, dict) else "invalid-request",
                trace_id=str(request.get("trace_id") or f"trace-{uuid4().hex}") if isinstance(request, dict) else f"trace-{uuid4().hex}",
                agent_id=str(request.get("agent_id", "unknown-agent")) if isinstance(request, dict) else "unknown-agent",
            )
            return None, ExecutionResultBuilder.failed(
                fallback,
                [],
                ExecutionError(
                    code="EXECUTION_REQUEST_INVALID",
                    message="Execution request validation failed",
                    details={"errors": exc.errors(include_url=False)},
                ),
            )
