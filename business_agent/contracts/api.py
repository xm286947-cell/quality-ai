from __future__ import annotations

from typing import Any

from pydantic import Field

from .common import ContractModel, ErrorDetail
from .execution import ExecutionResult


class ErrorBody(ErrorDetail):
    request_id: str = ""


class ErrorResponse(ContractModel):
    error: ErrorBody


class HealthResponse(ContractModel):
    status: str
    service: str
    version: str
    api_version: str


class AgentSummary(ContractModel):
    agent_id: str
    name: str = ""
    version: str = ""
    description: str = ""


class AgentListResponse(ContractModel):
    agents: list[Any] = Field(default_factory=list)


class ExecutionResponse(ExecutionResult):
    """HTTP response model. Retains legacy fields while adding contract metadata."""
