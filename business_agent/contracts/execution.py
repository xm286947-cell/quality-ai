from __future__ import annotations

from typing import Any

from pydantic import Field, model_validator

from .common import ContractMetadata, ContractModel, ErrorDetail, ExecutionStatus, WarningDetail
from .trace import TraceContext
from .version import CONTRACT_VERSION


class ExecutionRequest(ContractModel):
    contract_version: str = CONTRACT_VERSION
    request_id: str = ""
    agent_id: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    options: dict[str, Any] = Field(default_factory=dict)
    metadata: ContractMetadata = Field(default_factory=ContractMetadata)

    @model_validator(mode="after")
    def validate_agent_id(self) -> "ExecutionRequest":
        if not self.agent_id:
            raise ValueError("agent_id must not be empty")
        return self


class ExecutionResult(ContractModel):
    contract_version: str = CONTRACT_VERSION
    request_id: str
    agent_id: str
    agent_version: str = ""
    status: ExecutionStatus
    output: dict[str, Any] = Field(default_factory=dict)
    warnings: list[WarningDetail] = Field(default_factory=list)
    error: ErrorDetail | None = None
    trace: TraceContext = Field(default_factory=TraceContext)
    trace_path: str = ""
    metadata: ContractMetadata = Field(default_factory=ContractMetadata)

    @model_validator(mode="after")
    def validate_error_state(self) -> "ExecutionResult":
        if self.status == ExecutionStatus.FAILED and self.error is None:
            raise ValueError("error is required when status is FAILED")
        if self.status != ExecutionStatus.FAILED and self.error is not None:
            raise ValueError("error is only allowed when status is FAILED")
        return self
