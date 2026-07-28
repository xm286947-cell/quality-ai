from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from business_agent.runtime import ExecutionRuntime


def _http_status(payload: dict[str, Any]) -> int:
    status = payload.get("status")
    if status in {"success", "partial_success"}:
        return 200
    error = payload.get("error") or {}
    code = error.get("code")
    if code == "EXECUTION_REQUEST_INVALID":
        return 400
    if code == "AGENT_NOT_FOUND":
        return 404
    if code in {"AGENT_DISABLED", "KNOWLEDGE_SERVICE_UNAVAILABLE"}:
        return 503
    return 500


def create_app(runtime: ExecutionRuntime | None = None) -> FastAPI:
    execution_runtime = runtime or ExecutionRuntime()
    application = FastAPI(
        title="Business Agent API",
        version="1.1.0",
        description="Execution HTTP Transport for QUALITY_AGENT_CONTRACT V1.1",
    )
    application.state.runtime = execution_runtime

    @application.get("/health")
    def health() -> dict[str, Any]:
        return {
            "status": "UP",
            "capability": "business_agent",
            "contract_version": "V1.1",
            "transport": "http",
        }

    @application.post("/v1/executions")
    def execute(payload: dict[str, Any]) -> JSONResponse:
        response = application.state.runtime.execute(payload).model_dump(mode="json")
        return JSONResponse(status_code=_http_status(response), content=response)

    return application


app = create_app()
