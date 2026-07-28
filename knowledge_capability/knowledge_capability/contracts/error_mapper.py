from __future__ import annotations

from typing import Any

from knowledge_capability.contracts.models import ContractError


class BusinessAgentErrorMapper:
    @staticmethod
    def to_dict(error: ContractError | None) -> dict[str, Any] | None:
        if error is None:
            return None
        return {
            "code": error.code,
            "message": error.message,
            "details": dict(error.details),
            "retryable": bool(error.retryable),
        }
