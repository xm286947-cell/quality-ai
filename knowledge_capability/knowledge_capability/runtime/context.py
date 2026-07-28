from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from knowledge_capability.contracts import KnowledgeRequest


@dataclass
class RuntimeContext:
    request: KnowledgeRequest
    registration: Any = None
    profile: Any = None
    source: Any = None
    repository: Any = None
    provider: Any = None
    runtime_options: dict[str, Any] = field(default_factory=dict)

    @property
    def request_id(self) -> str:
        return self.request.request_id

    @property
    def service_id(self) -> str:
        return self.request.service_id
