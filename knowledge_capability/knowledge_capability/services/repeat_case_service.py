from __future__ import annotations

from typing import Any

from knowledge_capability.contracts import Evidence, KnowledgeRequest, KnowledgeResponse, TraceEntry
from knowledge_capability.repository import KnowledgeRepository


class RepeatCaseKnowledgeService:
    """Exposes the existing Repeat Case retrieval through the platform repository boundary."""

    def __init__(self, repository: KnowledgeRepository) -> None:
        self.repository = repository

    def handle(self, request: KnowledgeRequest) -> KnowledgeResponse:
        repository_result = self.repository.search(
            request.query,
            filters=request.filters,
            options=request.options,
        )
        result = repository_result.payload
        evidence = self._build_evidence(result, repository_result.source_id)
        return KnowledgeResponse(
            request_id=request.request_id,
            service_id=request.service_id,
            result=result,
            evidence=evidence,
            trace=[
                TraceEntry(
                    stage="repository_resolution",
                    component="KnowledgeRepository",
                    status="success",
                    details={
                        "provider_type": repository_result.provider_type,
                        "source_id": repository_result.source_id,
                    },
                ),
                TraceEntry(
                    stage="retrieve",
                    component="CaseRetriever",
                    status="success",
                    details={"result_count": repository_result.result_count},
                ),
            ],
        )

    @staticmethod
    def _build_evidence(result: dict[str, Any], source_id: str) -> list[Evidence]:
        evidence: list[Evidence] = []
        for index, item in enumerate(result.get("results") or []):
            case_id = str(item.get("case_id") or item.get("id") or f"result-{index + 1}")
            evidence.append(
                Evidence(
                    evidence_id=f"repeat-case:{case_id}",
                    source_type="repeat_case",
                    source_ref=case_id,
                    summary=str(item.get("problem_summary") or item.get("problem_description") or ""),
                    metadata={
                        "rank": index + 1,
                        "score": item.get("score"),
                        "source_id": source_id,
                    },
                )
            )
        return evidence
