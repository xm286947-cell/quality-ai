from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RuntimeErrorInfo:
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    retryable: bool = False


class KnowledgeRuntimeError(RuntimeError):
    code = "RUNTIME_ERROR"

    def __init__(self, message: str, *, details: dict[str, Any] | None = None, retryable: bool = False) -> None:
        super().__init__(message)
        self.info = RuntimeErrorInfo(self.code, message, details or {}, retryable)


class ContractRuntimeError(KnowledgeRuntimeError):
    code = "CONTRACT_ERROR"


class ProfileRuntimeError(KnowledgeRuntimeError):
    code = "PROFILE_ERROR"


class SourceRuntimeError(KnowledgeRuntimeError):
    code = "SOURCE_ERROR"


class RepositoryRuntimeError(KnowledgeRuntimeError):
    code = "REPOSITORY_ERROR"


class ProviderRuntimeError(KnowledgeRuntimeError):
    code = "PROVIDER_ERROR"


class RetrievalRuntimeError(KnowledgeRuntimeError):
    code = "RETRIEVAL_ERROR"
