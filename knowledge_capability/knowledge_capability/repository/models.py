from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RepositorySearchResult:
    """Platform-neutral repository result returned to the service layer."""

    payload: dict[str, Any]
    provider_type: str
    source_id: str
    result_count: int = 0
    details: dict[str, Any] = field(default_factory=dict)
