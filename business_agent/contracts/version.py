from __future__ import annotations

from pydantic import Field

from .common import ContractModel

CONTRACT_VERSION = "V1.0"
MODEL_VERSION = "1.2.0"
SUPPORTED_CONTRACT_VERSIONS = frozenset({CONTRACT_VERSION})


class ContractVersion(ContractModel):
    contract_version: str = Field(default=CONTRACT_VERSION)
    model_version: str = Field(default=MODEL_VERSION)
