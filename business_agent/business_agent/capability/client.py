from __future__ import annotations

from typing import Any, Protocol


class CapabilityClient(Protocol):
    def invoke(
        self,
        operation: str,
        request: dict[str, Any],
        *,
        timeout_ms: int,
    ) -> dict[str, Any]:
        """Invoke a capability operation and return the decoded response envelope."""
        ...
