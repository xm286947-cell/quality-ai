from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NodeRuntimePolicy:
    on_failure: str = "stop"
    allow_partial_success: bool = True

    @classmethod
    def from_mapping(cls, value: dict[str, Any] | None) -> "NodeRuntimePolicy":
        payload = value or {}
        on_failure = str(payload.get("on_failure", "stop")).strip().lower()
        if on_failure not in {"stop", "continue", "skip"}:
            raise ValueError(f"Unsupported on_failure policy: {on_failure}")
        return cls(
            on_failure=on_failure,
            allow_partial_success=bool(payload.get("allow_partial_success", True)),
        )
