from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from common.config_loader import ConfigError


@dataclass(frozen=True)
class ServiceProfile:
    service_id: str
    version: str
    status: str
    service_type: str
    schema: dict[str, Any]
    provider: dict[str, Any]
    adapter: dict[str, Any]
    parser: dict[str, Any]
    retrieval: dict[str, Any]
    result_mapping: dict[str, Any]
    evidence: dict[str, Any]
    version_rule: dict[str, Any]
    permission: dict[str, Any]
    runtime: dict[str, Any]
    raw: dict[str, Any]

    def validate(self) -> None:
        if not self.service_id:
            raise ConfigError("Service Profile缺少service_id")
        if not self.service_type:
            raise ConfigError(f"Service Profile缺少service_type: {self.service_id}")
        if not self.adapter.get("type"):
            raise ConfigError(f"Service Profile缺少adapter.type: {self.service_id}")
        if not self.retrieval.get("strategy"):
            raise ConfigError(f"Service Profile缺少retrieval.strategy: {self.service_id}")
        parser_enabled = bool(self.parser.get("enabled", False))
        if parser_enabled and not self.parser.get("type"):
            raise ConfigError(f"Parser启用时必须配置parser.type: {self.service_id}")


class ServiceProfileLoader:
    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root).resolve()
        self.profile_dir = self.project_root / "config" / "knowledge_services"

    def load(self, profile_name: str) -> ServiceProfile:
        suffixes = (".yaml", ".yml")
        filename = profile_name if profile_name.endswith(suffixes) else f"{profile_name}.yaml"
        path = self.profile_dir / filename
        if not path.is_file():
            raise ConfigError(f"Service Profile不存在: {path}")
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception as exc:
            raise ConfigError(f"Service Profile读取失败: {path}: {exc}") from exc
        if not isinstance(raw, dict):
            raise ConfigError(f"Service Profile根节点必须是对象: {path}")
        profile = ServiceProfile(
            service_id=str(raw.get("service_id") or "").strip(),
            version=str(raw.get("version") or "1.0"),
            status=str(raw.get("status") or "active"),
            service_type=str(raw.get("service_type") or raw.get("schema", {}).get("type") or "").strip(),
            schema=dict(raw.get("schema") or {}),
            provider=dict(raw.get("provider") or {}),
            adapter=dict(raw.get("adapter") or {}),
            parser=dict(raw.get("parser") or {}),
            retrieval=dict(raw.get("retrieval") or {}),
            result_mapping=dict(raw.get("result_mapping") or {}),
            evidence=dict(raw.get("evidence") or {}),
            version_rule=dict(raw.get("version_rule") or {}),
            permission=dict(raw.get("permission") or {}),
            runtime=dict(raw.get("runtime") or {}),
            raw=raw,
        )
        profile.validate()
        return profile
