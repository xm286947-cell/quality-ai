from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class KnowledgeSource:
    source_id: str
    service_id: str
    provider_type: str
    location: str
    schema_type: str
    status: str = "active"
    version: str = "1.0"
    options: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.source_id:
            raise ValueError("Knowledge Source缺少source_id")
        if not self.service_id:
            raise ValueError(f"Knowledge Source缺少service_id: {self.source_id}")
        if not self.provider_type:
            raise ValueError(f"Knowledge Source缺少provider.type: {self.source_id}")
