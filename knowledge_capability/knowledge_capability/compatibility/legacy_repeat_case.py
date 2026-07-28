from __future__ import annotations

from typing import Any

from knowledge_capability.contracts import KnowledgeRequest
from knowledge_capability.framework import KnowledgeCapabilityRuntime


class LegacyRepeatCaseCompatibility:
    """Maps legacy flat query parameters to Knowledge Contract without changing callers."""

    def __init__(self, runtime: KnowledgeCapabilityRuntime) -> None:
        self.runtime = runtime

    def search(self, text: str, top_k: int | None = None, **kwargs: Any) -> dict[str, Any]:
        request = KnowledgeRequest(
            service_id="repeat_case_service",
            query={
                "text": text,
                "cause_description": kwargs.get("cause_description", ""),
                "solution": kwargs.get("solution", ""),
                "ipmt": kwargs.get("ipmt", ""),
                "spdt": kwargs.get("spdt", ""),
                "responsible_department_level2": kwargs.get("department", ""),
                "cause_level1": kwargs.get("cause_level1", ""),
                "cause_level2": kwargs.get("cause_level2", ""),
            },
            filters={
                "product": kwargs.get("product", ""),
                "domain": kwargs.get("domain", ""),
            },
            options={"top_k": top_k} if top_k is not None else {},
            caller={"type": "legacy_repeat_case"},
        )
        response = self.runtime.query(request)
        if response.error is not None:
            raise RuntimeError(f"{response.error.code}: {response.error.message}")
        return response.result
