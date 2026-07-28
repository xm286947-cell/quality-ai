from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from knowledge_capability.adapters import BusinessAgentAdapter
from knowledge_capability.runtime import build_runtime


def _default_project_root() -> Path:
    configured = os.getenv("KC_PROJECT_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(__file__).resolve().parents[2]


def _http_status(payload: dict[str, Any]) -> int:
    if payload.get("success"):
        return 200
    error = payload.get("error") or {}
    code = error.get("code")
    if code == "INVALID_REQUEST":
        return 400
    if code == "SERVICE_NOT_FOUND":
        return 404
    if code in {"PROFILE_ERROR", "SOURCE_ERROR", "PROVIDER_ERROR", "REPOSITORY_ERROR"}:
        return 503
    return 500


def create_app(project_root: str | Path | None = None) -> FastAPI:
    root = Path(project_root).resolve() if project_root is not None else _default_project_root()
    runtime = build_runtime(root)
    adapter = BusinessAgentAdapter(runtime)

    application = FastAPI(
        title="Knowledge Capability API",
        version="1.1.0",
        description="HTTP Transport for QUALITY_AGENT_CONTRACT V1.0",
    )
    application.state.project_root = root
    application.state.adapter = adapter

    @application.get("/health")
    def health() -> dict[str, Any]:
        return {
            "status": "UP",
            "capability": "knowledge_capability",
            "contract_version": "V1.0",
            "transport": "http",
        }

    @application.post("/v1/knowledge/query")
    def query(payload: dict[str, Any]) -> JSONResponse:
        response = application.state.adapter.execute(payload)
        return JSONResponse(status_code=_http_status(response), content=response)

    return application


app = create_app()
