from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class KnowledgeRequest:
    """Stable external request contract for all knowledge services."""

    service_id: str
    query: dict[str, Any]
    request_id: str = field(default_factory=lambda: uuid4().hex)
    filters: dict[str, Any] = field(default_factory=dict)
    requested_fields: list[str] = field(default_factory=list)
    options: dict[str, Any] = field(default_factory=dict)
    caller: dict[str, Any] = field(default_factory=dict)
    contract_version: str = "1.0"

    def validate(self) -> None:
        if not self.service_id.strip():
            raise ValueError("service_id不能为空")
        if not isinstance(self.query, dict):
            raise ValueError("query必须是对象")
        if self.contract_version not in {"1.0", "V1.0"}:
            raise ValueError(f"不支持的contract_version: {self.contract_version}")
        if not isinstance(self.filters, dict):
            raise ValueError("filters必须是对象")
        if not isinstance(self.options, dict):
            raise ValueError("options必须是对象")
        if not isinstance(self.caller, dict):
            raise ValueError("caller必须是对象")


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    source_type: str
    source_ref: str
    summary: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TraceEntry:
    stage: str
    component: str
    status: str
    started_at: str = field(default_factory=_utc_now)
    finished_at: str = ""
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ContractError:
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    retryable: bool = False


@dataclass
class KnowledgeResponse:
    request_id: str
    service_id: str
    result: Any = None
    evidence: list[Evidence] = field(default_factory=list)
    trace: list[TraceEntry] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    error: ContractError | None = None
    contract_version: str = "1.0"
    created_at: str = field(default_factory=_utc_now)

    @property
    def success(self) -> bool:
        return self.error is None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
