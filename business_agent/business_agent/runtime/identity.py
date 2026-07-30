from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class RuntimeIdentity:
    trace_id: str
    execution_id: str
    request_id: str
    agent_id: str
    agent_version: str
    tenant_id: str = ""
    domain_id: str = ""
    user_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        agent_id: str,
        agent_version: str,
        request_id: str = "",
        tenant_id: str = "",
        domain_id: str = "",
        user_id: str = "",
    ) -> "RuntimeIdentity":
        return cls(
            trace_id=f"trace-{uuid4().hex}",
            execution_id=f"exec-{uuid4().hex}",
            request_id=request_id or f"req-{uuid4().hex}",
            agent_id=agent_id,
            agent_version=agent_version,
            tenant_id=tenant_id,
            domain_id=domain_id,
            user_id=user_id,
        )
