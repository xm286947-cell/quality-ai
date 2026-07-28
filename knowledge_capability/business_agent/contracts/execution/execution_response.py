from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .execution_artifact import ExecutionArtifact
from .execution_error import ExecutionError
from .execution_trace import ExecutionTrace


class ExecutionResponse(BaseModel):
    """Business Agent -> Client execution response."""

    model_config = ConfigDict(extra="forbid")

    contract_version: str = "V1.1"
    request_id: str
    trace_id: str
    agent_id: str
    status: Literal["success", "partial_success", "failed"]
    result: dict[str, Any] = Field(default_factory=dict)
    artifacts: list[ExecutionArtifact] = Field(default_factory=list)
    trace: list[ExecutionTrace] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    error: ExecutionError | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def success(self) -> bool:
        return self.status in {"success", "partial_success"}
