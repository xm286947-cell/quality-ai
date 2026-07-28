from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from common.config_loader import ConfigError


@dataclass(frozen=True)
class ServiceCatalogEntry:
    service_id: str
    version: str
    status: str
    profile_name: str
    factory: str
    options: dict[str, Any]


class ServiceCatalogLoader:
    """Loads platform service registrations without embedding business services in bootstrap."""

    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root).resolve()
        self.path = self.project_root / "config" / "knowledge_services" / "registry.yaml"

    def load(self) -> list[ServiceCatalogEntry]:
        if not self.path.is_file():
            raise ConfigError(f"Service Registry配置不存在: {self.path}")
        try:
            raw = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        except Exception as exc:
            raise ConfigError(f"Service Registry配置读取失败: {self.path}: {exc}") from exc
        services = raw.get("services") if isinstance(raw, dict) else None
        if not isinstance(services, list):
            raise ConfigError(f"Service Registry配置必须包含services列表: {self.path}")
        entries: list[ServiceCatalogEntry] = []
        seen: set[str] = set()
        for index, item in enumerate(services):
            if not isinstance(item, dict):
                raise ConfigError(f"services[{index}]必须是对象")
            service_id = str(item.get("service_id") or "").strip()
            if not service_id:
                raise ConfigError(f"services[{index}]缺少service_id")
            if service_id in seen:
                raise ConfigError(f"Service Registry配置重复: {service_id}")
            seen.add(service_id)
            factory = str(item.get("factory") or "").strip()
            if not factory:
                raise ConfigError(f"Service Registry配置缺少factory: {service_id}")
            entries.append(
                ServiceCatalogEntry(
                    service_id=service_id,
                    version=str(item.get("version") or "1.0"),
                    status=str(item.get("status") or "active"),
                    profile_name=str(item.get("profile_name") or service_id),
                    factory=factory,
                    options=dict(item.get("options") or {}),
                )
            )
        return entries
