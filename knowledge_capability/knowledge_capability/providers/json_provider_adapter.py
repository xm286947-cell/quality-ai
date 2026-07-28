from __future__ import annotations

from pathlib import Path
from typing import Any

from common.config_loader import ConfigLoader
from knowledge_capability.repository.models import RepositorySearchResult
from knowledge_capability.sources.models import KnowledgeSource
from repositories.json_repository import JsonArtifactRepository
from retriever.case_retriever import CaseRetriever, QueryInput


class JsonProviderAdapter:
    """Provider adapter that reuses JsonArtifactRepository and CaseRetriever unchanged."""

    def __init__(self, project_root: str | Path, source: KnowledgeSource) -> None:
        self.project_root = Path(project_root).resolve()
        self.source = source
        self.artifacts = JsonArtifactRepository(self.project_root)
        loader = ConfigLoader(self.project_root)
        self.retriever = CaseRetriever(
            self.project_root,
            loader.load("app"),
            loader.load("model"),
            loader.load("retrieval"),
        )

    def search(
        self,
        query: dict[str, Any],
        *,
        filters: dict[str, Any] | None = None,
        options: dict[str, Any] | None = None,
    ) -> RepositorySearchResult:
        query_input = self._to_query_input(query, filters or {})
        top_k = (options or {}).get("top_k")
        payload = self.retriever.search(query_input, top_k=int(top_k) if top_k is not None else None)
        return RepositorySearchResult(
            payload=payload,
            provider_type="json_repository",
            source_id=self.source.source_id,
            result_count=len(payload.get("results") or []),
            details={"schema": self.source.schema_type, "source_version": self.source.version},
        )

    def get(self, knowledge_id: str) -> dict[str, Any] | None:
        if not knowledge_id.strip():
            return None
        candidates = [
            f"knowledge/standard_case/{knowledge_id}.json",
            f"knowledge/enriched_case/{knowledge_id}.json",
        ]
        path = self.artifacts.first_existing(candidates)
        return self.artifacts.load(path) if path is not None else None

    def list(self, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        del filters  # M1 boundary only; filtering belongs to later Knowledge Management.
        result: list[dict[str, Any]] = []
        for path in self.artifacts.list("knowledge/standard_case"):
            payload = self.artifacts.load(path)
            if payload is not None:
                result.append(payload)
        return result

    def metadata(self) -> dict[str, Any]:
        return {
            "source_id": self.source.source_id,
            "service_id": self.source.service_id,
            "provider_type": "json_repository",
            "location": self.source.location,
            "schema": self.source.schema_type,
            "status": self.source.status,
            "version": self.source.version,
        }

    @staticmethod
    def _to_query_input(query: dict[str, Any], filters: dict[str, Any]) -> QueryInput:
        organization = dict(query.get("organization") or {})
        classification = dict(query.get("classification") or {})
        merged_filters = dict(query.get("filters") or {})
        merged_filters.update(filters)
        return QueryInput(
            text=str(query.get("text") or query.get("problem_description") or ""),
            cause_description=str(query.get("cause_description") or ""),
            solution=str(query.get("solution") or ""),
            ipmt=str(organization.get("ipmt") or query.get("ipmt") or ""),
            spdt=str(organization.get("spdt") or query.get("spdt") or ""),
            responsible_department_level2=str(
                organization.get("responsible_department_level2")
                or query.get("responsible_department_level2")
                or ""
            ),
            product=str(merged_filters.get("product") or ""),
            domain=str(merged_filters.get("domain") or ""),
            cause_level1=str(classification.get("cause_level1") or query.get("cause_level1") or ""),
            cause_level2=str(classification.get("cause_level2") or query.get("cause_level2") or ""),
        )
