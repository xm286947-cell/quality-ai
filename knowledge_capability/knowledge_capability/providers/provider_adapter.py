from __future__ import annotations

from typing import Protocol

from knowledge_capability.repository.repository import KnowledgeRepository


class ProviderAdapter(KnowledgeRepository, Protocol):
    """Marker contract for provider-specific repository adapters."""
