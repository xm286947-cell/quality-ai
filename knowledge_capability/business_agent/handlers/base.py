from __future__ import annotations

from abc import ABC, abstractmethod

from business_agent.contracts.execution import ExecutionContext


class ExecutionHandler(ABC):
    """A single independently testable execution step."""

    name: str

    @abstractmethod
    def handle(self, context: ExecutionContext) -> ExecutionContext:
        raise NotImplementedError
