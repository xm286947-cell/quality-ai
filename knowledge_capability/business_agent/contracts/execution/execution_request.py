from __future__ import annotations

from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExecutionRequest(BaseModel):
    """Client -> Business Agent execution request."""

    model_config = ConfigDict(extra="forbid")

    contract_version: str = "V1.1"
    request_id: str = Field(default_factory=lambda: f"req-{uuid4().hex}")
    trace_id: str | None = None
    agent_id: str = Field(min_length=1)
    operation: str = Field(default="execute", min_length=1)
    input: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    options: dict[str, Any] = Field(default_factory=dict)
    caller: dict[str, Any] = Field(default_factory=dict)

    @field_validator("contract_version")
    @classmethod
    def validate_contract_version(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized in {"1.1", "V1.1"}:
            return "V1.1"
        raise ValueError("unsupported execution contract version; expected V1.1")
