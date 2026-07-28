from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ExecutionTrace(BaseModel):
    """One observable execution step."""

    model_config = ConfigDict(extra="forbid")

    step: str = Field(min_length=1)
    status: str = Field(default="success", min_length=1)
    started_at: datetime = Field(default_factory=utc_now)
    finished_at: datetime | None = None
    duration_ms: float | None = Field(default=None, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)
