from __future__ import annotations

from pathlib import Path

from knowledge_capability.framework import KnowledgeCapabilityRuntime
from knowledge_capability.profiles import ServiceProfileLoader
from knowledge_capability.registry import ServiceRegistration, ServiceRegistry
from knowledge_capability.runtime.service_catalog import ServiceCatalogLoader
from knowledge_capability.runtime.service_factory import ServiceFactory


def build_runtime(project_root: str | Path) -> KnowledgeCapabilityRuntime:
    root = Path(project_root).resolve()
    profile_loader = ServiceProfileLoader(root)
    catalog = ServiceCatalogLoader(root).load()
    factory = ServiceFactory()
    registry = ServiceRegistry()

    for entry in catalog:
        profile = profile_loader.load(entry.profile_name)
        if profile.service_id != entry.service_id:
            raise ValueError(
                f"Registry与Profile的service_id不一致: {entry.service_id} != {profile.service_id}"
            )
        registry.register(
            ServiceRegistration(
                service_id=entry.service_id,
                version=entry.version,
                status=entry.status,
                profile_name=entry.profile_name,
                handler=factory.create(root, entry, profile),
            )
        )
    return KnowledgeCapabilityRuntime(registry, profile_loader)
