from __future__ import annotations

from pathlib import Path
from typing import Callable

from knowledge_capability.profiles.loader import ServiceProfile
from knowledge_capability.registry.service_registry import KnowledgeServiceHandler
from knowledge_capability.repository import RepositoryFactory
from knowledge_capability.runtime.service_catalog import ServiceCatalogEntry
from knowledge_capability.services import RepeatCaseKnowledgeService
from knowledge_capability.sources import KnowledgeSourceRegistry

ServiceBuilder = Callable[[Path, ServiceCatalogEntry, ServiceProfile], KnowledgeServiceHandler]


class ServiceFactory:
    """M1 assembly factory that binds profiles, sources and existing engineering assets."""

    def __init__(self) -> None:
        self._builders: dict[str, ServiceBuilder] = {
            "repeat_case_existing": self._build_repeat_case,
        }

    def create(
        self,
        project_root: Path,
        entry: ServiceCatalogEntry,
        profile: ServiceProfile,
    ) -> KnowledgeServiceHandler:
        try:
            builder = self._builders[entry.factory]
        except KeyError as exc:
            raise ValueError(f"未知Service Factory: {entry.factory}") from exc
        return builder(project_root, entry, profile)

    @staticmethod
    def _build_repeat_case(
        project_root: Path,
        entry: ServiceCatalogEntry,
        profile: ServiceProfile,
    ) -> KnowledgeServiceHandler:
        source_id = str(profile.provider.get("source_id") or "").strip()
        source_registry = KnowledgeSourceRegistry(project_root)
        source = source_registry.get(source_id) if source_id else source_registry.get_for_service(entry.service_id)
        if source.service_id != entry.service_id:
            raise ValueError(
                f"Knowledge Source与Service不匹配: {source.source_id} -> {source.service_id}, expected {entry.service_id}"
            )
        repository = RepositoryFactory().create(project_root, profile, source)
        return RepeatCaseKnowledgeService(repository)
