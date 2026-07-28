from __future__ import annotations

from pathlib import Path

from knowledge_capability.profiles.loader import ServiceProfile
from knowledge_capability.providers.json_provider_adapter import JsonProviderAdapter
from knowledge_capability.repository.repository import KnowledgeRepository
from knowledge_capability.sources.models import KnowledgeSource


class RepositoryFactory:
    """Creates repository boundaries from Service Profile and Knowledge Source."""

    def create(
        self,
        project_root: str | Path,
        profile: ServiceProfile,
        source: KnowledgeSource,
    ) -> KnowledgeRepository:
        provider_type = str(profile.provider.get("type") or source.provider_type).strip()
        if provider_type in {"json", "json_repository"}:
            return JsonProviderAdapter(project_root, source)
        raise ValueError(f"不支持的Provider类型: {provider_type}")
