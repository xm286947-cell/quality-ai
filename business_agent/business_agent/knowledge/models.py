from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class KnowledgeEvidence:
    evidence_id: str = ""
    source_id: str = ""
    source_type: str = ""
    title: str = ""
    content: str = ""
    uri: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "KnowledgeEvidence":
        return cls(
            evidence_id=str(value.get("evidence_id") or value.get("id") or ""),
            source_id=str(value.get("source_id") or value.get("source_ref") or ""),
            source_type=str(value.get("source_type") or ""),
            title=str(value.get("title") or ""),
            content=str(value.get("content") or value.get("summary") or value.get("text") or ""),
            uri=str(value.get("uri") or value.get("url") or ""),
            metadata=dict(value.get("metadata") or {}),
        )


@dataclass(frozen=True)
class KnowledgeItem:
    knowledge_id: str
    score: float = 0.0
    title: str = ""
    content: str = ""
    knowledge_type: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    evidence: tuple[KnowledgeEvidence, ...] = field(default_factory=tuple)

    @classmethod
    def from_dict(
        cls,
        value: dict[str, Any],
        external_evidence: tuple[KnowledgeEvidence, ...] = (),
    ) -> "KnowledgeItem":
        raw_evidence = value.get("evidence") or value.get("evidences") or []
        item_id = str(value.get("knowledge_id") or value.get("case_id") or value.get("id") or "")
        item_evidence = tuple(KnowledgeEvidence.from_dict(x) for x in raw_evidence if isinstance(x, dict))
        if not item_evidence and external_evidence:
            matched = tuple(item for item in external_evidence if not item.source_id or item.source_id == item_id)
            item_evidence = matched or external_evidence
        return cls(
            knowledge_id=item_id,
            score=float(value.get("score") or 0.0),
            title=str(value.get("title") or value.get("problem_title") or ""),
            content=str(value.get("content") or value.get("summary") or value.get("text") or ""),
            knowledge_type=str(value.get("knowledge_type") or value.get("type") or "repeat_case"),
            metadata=dict(value.get("metadata") or {}),
            evidence=item_evidence,
        )


@dataclass(frozen=True)
class KnowledgeRequest:
    request_id: str
    service_id: str
    query: dict[str, Any]
    filters: dict[str, Any] = field(default_factory=dict)
    requested_fields: list[str] = field(default_factory=list)
    options: dict[str, Any] = field(default_factory=dict)
    caller: dict[str, Any] = field(default_factory=dict)
    contract_version: str = "V1.0"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class KnowledgeResponse:
    request_id: str
    status: str
    items: tuple[KnowledgeItem, ...] = field(default_factory=tuple)
    total: int = 0
    elapsed_ms: int = 0
    provider: str = ""
    error_code: str = ""
    error_message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    contract_version: str = "V1.0"
    service_id: str = ""
    trace: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "KnowledgeResponse":
        # QUALITY_AGENT_CONTRACT V1.0 response.
        if "success" in value or "result" in value or "evidence" in value:
            success = bool(value.get("success"))
            result = value.get("result") if isinstance(value.get("result"), dict) else {}
            raw_items = result.get("results") or result.get("items") or result.get("candidates") or []
            raw_evidence = value.get("evidence") or []
            evidence = tuple(KnowledgeEvidence.from_dict(x) for x in raw_evidence if isinstance(x, dict))
            error = value.get("error") if isinstance(value.get("error"), dict) else {}
            trace = tuple(x for x in (value.get("trace") or []) if isinstance(x, dict))
            elapsed_ms = 0
            for entry in trace:
                details = entry.get("details") if isinstance(entry.get("details"), dict) else {}
                elapsed_ms += int(details.get("elapsed_ms") or details.get("latency_ms") or 0)
            items = tuple(KnowledgeItem.from_dict(x, evidence) for x in raw_items if isinstance(x, dict))
            return cls(
                request_id=str(value.get("request_id") or ""),
                service_id=str(value.get("service_id") or ""),
                status="SUCCESS" if success else "FAILED",
                items=items,
                total=int(result.get("total") or result.get("count") or len(items)),
                elapsed_ms=elapsed_ms,
                provider=str(result.get("provider") or "knowledge_capability"),
                error_code=str(error.get("code") or ""),
                error_message=str(error.get("message") or ""),
                metadata={"result": result, "created_at": value.get("created_at")},
                contract_version=str(value.get("contract_version") or "V1.0"),
                trace=trace,
                warnings=tuple(str(x) for x in (value.get("warnings") or [])),
            )

        # Backward-compatible parser for local mock fixtures used before HTTP integration.
        data = value.get("data") if isinstance(value.get("data"), dict) else value
        raw_items = data.get("items") or data.get("results") or data.get("candidates") or []
        return cls(
            request_id=str(data.get("request_id") or value.get("request_id") or ""),
            status=str(data.get("status") or value.get("status") or "SUCCESS").upper(),
            items=tuple(KnowledgeItem.from_dict(x) for x in raw_items if isinstance(x, dict)),
            total=int(data.get("total") or len(raw_items)),
            elapsed_ms=int(data.get("elapsed_ms") or data.get("latency_ms") or 0),
            provider=str(data.get("provider") or value.get("provider") or ""),
            error_code=str(data.get("error_code") or value.get("error_code") or ""),
            error_message=str(data.get("error_message") or value.get("error_message") or ""),
            metadata=dict(data.get("metadata") or {}),
            contract_version=str(data.get("contract_version") or value.get("contract_version") or "V1.0"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
