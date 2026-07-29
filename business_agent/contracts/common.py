from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ContractModel(BaseModel):
    """Base model for all public BUSINESS_AGENT contracts."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True, str_strip_whitespace=True)


class ExecutionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    WARNING = "WARNING"
    FAILED = "FAILED"
    RUNNING = "RUNNING"
    SKIPPED = "SKIPPED"


class ContractMetadata(ContractModel):
    created_at: str = Field(default_factory=utc_now_iso)
    source: str = ""
    labels: dict[str, str] = Field(default_factory=dict)
    attributes: dict[str, Any] = Field(default_factory=dict)


class CallerIdentity(ContractModel):
    type: str = "business_agent"
    agent_id: str = ""
    agent_version: str = ""
    tenant_id: str = ""
    user_id: str = ""


class WarningDetail(ContractModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorDetail(ContractModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    retryable: bool = False


class TimingDetail(ContractModel):
    started_at: str = ""
    completed_at: str = ""
    elapsed_ms: float = Field(default=0.0, ge=0)


class CostDetail(ContractModel):
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)
    amount: float = Field(default=0.0, ge=0)
    currency: str = ""
