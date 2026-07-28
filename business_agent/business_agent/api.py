from __future__ import annotations

import json
import logging
import os
import re
import shutil
import time
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from business_agent.api_contract import AgentListResponse, ErrorResponse, ExecutionResponse, HealthResponse
from business_agent.models import RuntimeRequest
from business_agent.runtime.runtime import BusinessAgentRuntime

ROOT = Path(__file__).resolve().parents[1]
UPLOAD_ROOT = ROOT / "output" / "api_uploads"
MAX_UPLOAD_BYTES = int(os.getenv("BUSINESS_AGENT_MAX_UPLOAD_BYTES", str(50 * 1024 * 1024)))
API_VERSION = "v1"
SERVICE_VERSION = "1.1"
ALLOWED_SUFFIXES = {".xlsx", ".xls", ".json", ".jsonl", ".csv", ".md", ".txt", ".pdf", ".docx", ".zip"}

logger = logging.getLogger("business_agent.api")

app = FastAPI(
    title="BUSINESS_AGENT_ENGINE API",
    version=SERVICE_VERSION,
    description=(
        "Execution API for QUALITY_AGENT Business Agent runtime. "
        "Client uploads are accepted through multipart/form-data; knowledge calls remain JSON contracts."
    ),
    openapi_tags=[
        {"name": "system", "description": "Service health and metadata."},
        {"name": "agents", "description": "Agent discovery and execution."},
    ],
)


def _request_id_from_request(request: Request) -> str:
    return str(getattr(request.state, "request_id", "") or request.headers.get("X-Request-ID", "")).strip()


def _error_response(status_code: int, code: str, message: str, request_id: str = "", details: dict[str, Any] | None = None) -> JSONResponse:
    body = {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "request_id": request_id,
        }
    }
    return JSONResponse(status_code=status_code, content=body, headers={"X-API-Version": API_VERSION})


@app.middleware("http")
async def request_context_and_logging(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", "").strip() or f"REQ-{uuid.uuid4().hex[:12].upper()}"
    request.state.request_id = request_id
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        logger.exception("request_failed request_id=%s method=%s path=%s elapsed_ms=%s", request_id, request.method, request.url.path, elapsed_ms)
        raise
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    response.headers.setdefault("X-Request-ID", str(getattr(request.state, "request_id", "") or request_id))
    response.headers["X-API-Version"] = API_VERSION
    logger.info(
        "request_completed request_id=%s method=%s path=%s status=%s elapsed_ms=%s",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return _error_response(
        422,
        "EXECUTION_REQUEST_VALIDATION_FAILED",
        "Execution request validation failed.",
        _request_id_from_request(request),
        {"errors": exc.errors()},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail
    if isinstance(detail, dict):
        code = str(detail.get("code") or "HTTP_ERROR")
        message = str(detail.get("message") or code)
        details = dict(detail.get("details") or {})
    else:
        text = str(detail)
        if ":" in text:
            code, message = text.split(":", 1)
            code, message = code.strip(), message.strip()
        else:
            code, message = text.strip() or "HTTP_ERROR", text.strip() or "HTTP error"
        details = {}
    return _error_response(exc.status_code, code, message, _request_id_from_request(request), details)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_exception request_id=%s", _request_id_from_request(request))
    return _error_response(
        500,
        "INTERNAL_SERVER_ERROR",
        "Unexpected server error.",
        _request_id_from_request(request),
    )


def _safe_filename(filename: str | None) -> str:
    value = Path(filename or "input.xlsx").name
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value)
    return value or "input.xlsx"


def _validate_upload_name(filename: str | None) -> None:
    safe_name = _safe_filename(filename)
    suffix = Path(safe_name).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(
            status_code=415,
            detail={
                "code": "UNSUPPORTED_INPUT_TYPE",
                "message": f"Unsupported upload type: {suffix or '<none>'}",
                "details": {"allowed_suffixes": sorted(ALLOWED_SUFFIXES)},
            },
        )


def _parse_options(options_json: str | None) -> dict[str, Any]:
    if not options_json:
        return {}
    try:
        value = json.loads(options_json)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_OPTIONS_JSON", "message": "options_json is not valid JSON.", "details": {"reason": str(exc)}},
        ) from exc
    if not isinstance(value, dict):
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_OPTIONS_JSON", "message": "options_json must be a JSON object."},
        )
    return value


async def _save_upload(upload: UploadFile, request_id: str) -> tuple[Path, int]:
    _validate_upload_name(upload.filename)
    request_dir = UPLOAD_ROOT / request_id
    request_dir.mkdir(parents=True, exist_ok=True)
    destination = request_dir / _safe_filename(upload.filename)
    total = 0
    try:
        with destination.open("wb") as handle:
            while True:
                chunk = await upload.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail={
                            "code": "INPUT_TOO_LARGE",
                            "message": "Uploaded file exceeds the configured size limit.",
                            "details": {"max_bytes": MAX_UPLOAD_BYTES},
                        },
                    )
                handle.write(chunk)
        if total == 0:
            raise HTTPException(status_code=400, detail={"code": "EMPTY_INPUT_FILE", "message": "Uploaded file is empty."})
    except Exception:
        shutil.rmtree(request_dir, ignore_errors=True)
        raise
    finally:
        await upload.close()
    return destination, total


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> dict[str, Any]:
    return {"status": "UP", "service": "business_agent", "version": SERVICE_VERSION, "api_version": API_VERSION}


@app.get("/v1/agents", response_model=AgentListResponse, tags=["agents"])
def list_agents() -> dict[str, Any]:
    return {"agents": BusinessAgentRuntime(ROOT).list_agents()}


@app.post(
    "/v1/agents/{agent_id}/run",
    response_model=ExecutionResponse,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 413: {"model": ErrorResponse}, 415: {"model": ErrorResponse}, 422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["agents"],
)
async def run_agent(
    request: Request,
    agent_id: str,
    file: UploadFile = File(..., description="Business input artifact."),
    request_id: str = Form(default=""),
    query_id: str = Form(default=""),
    top_k: int = Form(default=5, ge=1, le=100),
    overwrite: bool = Form(default=True),
    mock: bool = Form(default=False),
    skip_ai: bool = Form(default=False),
    options_json: str = Form(default=""),
    knowledge_provider: str = Form(default="http"),
    knowledge_base_url: str = Form(default=""),
    knowledge_endpoint: str = Form(default="/v1/knowledge/query"),
    knowledge_timeout_seconds: float = Form(default=30.0, gt=0, le=300),
) -> JSONResponse:
    actual_request_id = request_id.strip() or _request_id_from_request(request) or f"RUN-{uuid.uuid4().hex[:12].upper()}"
    request.state.request_id = actual_request_id
    source, file_size = await _save_upload(file, actual_request_id)
    options = _parse_options(options_json)
    knowledge_options = dict(options.get("knowledge") or {})
    provider = knowledge_provider.strip().lower() or "http"
    if provider not in {"http", "capability", "mock"}:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "UNSUPPORTED_KNOWLEDGE_PROVIDER",
                "message": f"Unsupported knowledge_provider: {provider}",
                "details": {"supported": ["http", "capability", "mock"]},
            },
        )
    knowledge_options["provider"] = provider
    if knowledge_base_url.strip():
        knowledge_options["base_url"] = knowledge_base_url.strip().rstrip("/")
    if knowledge_endpoint.strip():
        knowledge_options["endpoint"] = knowledge_endpoint.strip()
    knowledge_options["timeout_seconds"] = knowledge_timeout_seconds
    options["knowledge"] = knowledge_options
    inputs: dict[str, Any] = {
        "input": str(source),
        "top_k": top_k,
        "overwrite": overwrite,
        "mock": mock,
        "skip_ai": skip_ai,
    }
    if query_id.strip():
        inputs["query_id"] = query_id.strip()

    logger.info(
        "agent_execution_started request_id=%s agent_id=%s filename=%s file_size=%s top_k=%s knowledge_provider=%s",
        actual_request_id,
        agent_id,
        source.name,
        file_size,
        top_k,
        provider,
    )
    try:
        result = BusinessAgentRuntime(ROOT).run(
            RuntimeRequest(agent_id=agent_id, request_id=actual_request_id, inputs=inputs, options=options)
        )
        return JSONResponse(status_code=200, content=asdict(result), headers={"X-Request-ID": actual_request_id, "X-API-Version": API_VERSION})
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail={"code": "INPUT_NOT_FOUND", "message": str(exc)}) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"code": "INVALID_EXECUTION_REQUEST", "message": str(exc)}) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail={"code": "AGENT_NOT_FOUND", "message": f"Agent not found: {agent_id}"}) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={"code": "AGENT_EXECUTION_FAILED", "message": "Agent execution failed.", "details": {"reason": str(exc)}},
        ) from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "business_agent.api:app",
        host=os.getenv("BUSINESS_AGENT_HOST", "0.0.0.0"),
        port=int(os.getenv("BUSINESS_AGENT_PORT", "8080")),
        reload=False,
    )
