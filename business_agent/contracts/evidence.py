from __future__ import annotations

from typing import Any

from pydantic import Field

from .common import ContractModel


class EvidenceReference(ContractModel):
    evidence_id: str = ""
    source_id: str = ""
    source_type: str = ""
    title: str = ""
    content: str = ""
    uri: str = ""
    locator: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
