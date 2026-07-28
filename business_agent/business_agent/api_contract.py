from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    request_id: str = ""


class ErrorResponse(BaseModel):
    error: ErrorBody


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    api_version: str


class AgentSummary(BaseModel):
    agent_id: str
    name: str = ""
    version: str = ""
    description: str = ""


class AgentListResponse(BaseModel):
    agents: list[Any]


class ExecutionResponse(BaseModel):
    request_id: str
    agent_id: str
    agent_version: str
    status: str
    output: dict[str, Any]
    trace_path: str
