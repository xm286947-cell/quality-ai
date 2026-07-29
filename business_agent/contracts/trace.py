from __future__ import annotations

from typing import Any

from pydantic import Field

from .common import ContractModel, CostDetail, ExecutionStatus, TimingDetail


class TraceEntry(ContractModel):
    name: str
    type: str = "runtime"
    status: ExecutionStatus = ExecutionStatus.SUCCESS
    provider: str = ""
    timing: TimingDetail = Field(default_factory=TimingDetail)
    cost: CostDetail = Field(default_factory=CostDetail)
    details: dict[str, Any] = Field(default_factory=dict)


class TraceContext(ContractModel):
    trace_id: str = ""
    request_id: str = ""
    entries: list[TraceEntry] = Field(default_factory=list)
    debug: dict[str, Any] = Field(default_factory=dict)
