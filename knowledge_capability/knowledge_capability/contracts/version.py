from __future__ import annotations

CONTRACT_NAME = "QUALITY_AGENT_CONTRACT"
CONTRACT_SCOPE = "Business Agent ↔ Knowledge Capability Contract"
CONTRACT_VERSION = "V1.0"
_INTERNAL_CONTRACT_VERSION = "1.0"


def normalize_contract_version(value: str | None) -> str:
    normalized = str(value or "").strip().upper()
    if normalized in {"1.0", "V1.0"}:
        return CONTRACT_VERSION
    return normalized


def is_supported_contract_version(value: str | None) -> bool:
    return normalize_contract_version(value) == CONTRACT_VERSION


def to_internal_contract_version(value: str | None) -> str:
    if not is_supported_contract_version(value):
        raise ValueError(f"不支持的Contract版本: {value!r}，当前仅支持{CONTRACT_VERSION}")
    return _INTERNAL_CONTRACT_VERSION
