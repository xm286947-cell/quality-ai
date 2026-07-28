from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from knowledge_capability.contracts.version import CONTRACT_VERSION, is_supported_contract_version


class ContractValidationError(ValueError):
    """Raised when a Business Agent contract payload is invalid."""


class BusinessAgentContractValidator:
    REQUIRED_FIELDS = ("service_id", "query")

    @classmethod
    def validate_request(cls, payload: Mapping[str, Any]) -> None:
        if not isinstance(payload, Mapping):
            raise ContractValidationError("Business Agent请求必须是对象")
        missing = [field for field in cls.REQUIRED_FIELDS if field not in payload]
        if missing:
            raise ContractValidationError(f"缺少必填字段: {', '.join(missing)}")
        if not is_supported_contract_version(payload.get("contract_version", CONTRACT_VERSION)):
            raise ContractValidationError(
                f"不支持的contract_version: {payload.get('contract_version')!r}，当前仅支持{CONTRACT_VERSION}"
            )
        service_id = payload.get("service_id")
        if not isinstance(service_id, str) or not service_id.strip():
            raise ContractValidationError("service_id不能为空")
        if not isinstance(payload.get("query"), Mapping):
            raise ContractValidationError("query必须是对象")
        for field in ("filters", "options", "caller"):
            value = payload.get(field, {})
            if value is not None and not isinstance(value, Mapping):
                raise ContractValidationError(f"{field}必须是对象")
        requested_fields = payload.get("requested_fields", [])
        if requested_fields is not None and not isinstance(requested_fields, list):
            raise ContractValidationError("requested_fields必须是数组")

    @classmethod
    def validate_response(cls, payload: Mapping[str, Any]) -> None:
        if not isinstance(payload, Mapping):
            raise ContractValidationError("Knowledge Capability响应必须是对象")
        for field in ("request_id", "service_id", "success", "contract_version"):
            if field not in payload:
                raise ContractValidationError(f"响应缺少必填字段: {field}")
        if not isinstance(payload.get("success"), bool):
            raise ContractValidationError("响应success必须是布尔值")
        if not is_supported_contract_version(payload.get("contract_version")):
            raise ContractValidationError("响应contract_version不兼容")
        if payload.get("success") and payload.get("error") is not None:
            raise ContractValidationError("成功响应不能包含error")
        if not payload.get("success") and not isinstance(payload.get("error"), Mapping):
            raise ContractValidationError("失败响应必须包含error对象")
