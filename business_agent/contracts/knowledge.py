from __future__ import annotations

from typing import Any

from pydantic import Field, model_validator

from .common import CallerIdentity, ContractMetadata, ContractModel, ErrorDetail, ExecutionStatus, WarningDetail
from .evidence import EvidenceReference
from .trace import TraceContext
from .version import CONTRACT_VERSION


class KnowledgeQuery(ContractModel):
    text: str = ""
    fields: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_query(self) -> "KnowledgeQuery":
        if not self.text and not self.fields:
            raise ValueError("knowledge query requires text or fields")
        return self


class KnowledgeRequestContract(ContractModel):
    contract_version: str = CONTRACT_VERSION
    request_id: str
    service_id: str
    query: KnowledgeQuery
    filters: dict[str, Any] = Field(default_factory=dict)
    requested_fields: list[str] = Field(default_factory=list)
    options: dict[str, Any] = Field(default_factory=dict)
    caller: CallerIdentity = Field(default_factory=CallerIdentity)
    metadata: ContractMetadata = Field(default_factory=ContractMetadata)


class KnowledgeItemContract(ContractModel):
    knowledge_id: str
    score: float = Field(default=0.0, ge=0)
    title: str = ""
    content: str = ""
    knowledge_type: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    evidence: list[EvidenceReference] = Field(default_factory=list)


class KnowledgeResponseContract(ContractModel):
    contract_version: str = CONTRACT_VERSION
    request_id: str
    service_id: str = ""
    status: ExecutionStatus
    items: list[KnowledgeItemContract] = Field(default_factory=list)
    total: int = Field(default=0, ge=0)
    provider: str = ""
    warnings: list[WarningDetail] = Field(default_factory=list)
    error: ErrorDetail | None = None
    trace: TraceContext = Field(default_factory=TraceContext)
    metadata: ContractMetadata = Field(default_factory=ContractMetadata)

    @model_validator(mode="after")
    def validate_response(self) -> "KnowledgeResponseContract":
        if self.total < len(self.items):
            raise ValueError("total must be greater than or equal to item count")
        if self.status == ExecutionStatus.FAILED and self.error is None:
            raise ValueError("error is required when status is FAILED")
        return self
