from __future__ import annotations

from typing import Any, Protocol

from knowledge_capability.repository.models import RepositorySearchResult


class KnowledgeRepository(Protocol):
    """Stable access boundary shared by management and retrieval capabilities."""

    def search(
        self,
        query: dict[str, Any],
        *,
        filters: dict[str, Any] | None = None,
        options: dict[str, Any] | None = None,
    ) -> RepositorySearchResult: ...

    def get(self, knowledge_id: str) -> dict[str, Any] | None: ...

    def list(self, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]: ...

    def metadata(self) -> dict[str, Any]: ...
