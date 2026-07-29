from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from business_agent.contracts.version import SUPPORTED_CONTRACT_VERSIONS

T = TypeVar("T", bound=BaseModel)


class ContractValidationError(ValueError):
    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


class ContractValidator:
    @staticmethod
    def validate_version(payload: dict[str, Any]) -> None:
        version = str(payload.get("contract_version") or "")
        if version not in SUPPORTED_CONTRACT_VERSIONS:
            raise ContractValidationError(
                "UNSUPPORTED_CONTRACT_VERSION",
                f"Unsupported contract_version: {version or '<empty>'}",
                {"supported_versions": sorted(SUPPORTED_CONTRACT_VERSIONS)},
            )

    @classmethod
    def validate(cls, model: type[T], payload: dict[str, Any], *, check_version: bool = True) -> T:
        if check_version:
            cls.validate_version(payload)
        try:
            return model.model_validate(payload)
        except ValidationError as exc:
            raise ContractValidationError(
                "CONTRACT_VALIDATION_FAILED",
                "Contract validation failed.",
                {"errors": exc.errors(include_url=False)},
            ) from exc
