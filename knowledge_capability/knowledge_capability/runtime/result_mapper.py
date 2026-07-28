from __future__ import annotations

from knowledge_capability.contracts import ContractError, KnowledgeResponse
from common.config_loader import ConfigError
from knowledge_capability.runtime.errors import KnowledgeRuntimeError


class ResultMapper:
    @staticmethod
    def success(response: KnowledgeResponse, trace: list) -> KnowledgeResponse:
        response.trace = trace + response.trace
        return response

    @staticmethod
    def failure(request, trace: list, error: Exception) -> KnowledgeResponse:
        if isinstance(error, KnowledgeRuntimeError):
            info = error.info
            contract_error = ContractError(info.code, info.message, info.details, info.retryable)
        elif isinstance(error, ConfigError):
            contract_error = ContractError("PROFILE_ERROR", str(error), {"error_type": type(error).__name__})
        elif isinstance(error, KeyError):
            contract_error = ContractError("SERVICE_NOT_FOUND", str(error))
        elif isinstance(error, ValueError):
            contract_error = ContractError("INVALID_REQUEST", str(error))
        else:
            contract_error = ContractError("SERVICE_EXECUTION_FAILED", str(error), {"error_type": type(error).__name__})
        return KnowledgeResponse(request_id=request.request_id, service_id=request.service_id, trace=trace, error=contract_error)
