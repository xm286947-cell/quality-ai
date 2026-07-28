from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from business_agent.handlers import ExecutionHandler


@dataclass(frozen=True)
class AgentDefinition:
    """Runtime definition for one registered Business Agent."""

    agent_id: str
    handlers: tuple[ExecutionHandler, ...]
    enabled: bool = True
    description: str = ""

    @classmethod
    def create(
        cls,
        agent_id: str,
        handlers: Iterable[ExecutionHandler],
        *,
        enabled: bool = True,
        description: str = "",
    ) -> "AgentDefinition":
        normalized_id = agent_id.strip()
        if not normalized_id:
            raise ValueError("agent_id must not be empty")
        normalized_handlers = tuple(handlers)
        if not normalized_handlers:
            raise ValueError("agent definition requires at least one handler")
        return cls(
            agent_id=normalized_id,
            handlers=normalized_handlers,
            enabled=enabled,
            description=description,
        )
