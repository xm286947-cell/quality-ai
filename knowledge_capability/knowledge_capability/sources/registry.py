from __future__ import annotations

from pathlib import Path

import yaml

from common.config_loader import ConfigError
from knowledge_capability.sources.models import KnowledgeSource


class KnowledgeSourceRegistry:
    """Configuration-backed source registry for platform knowledge services."""

    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root).resolve()
        self.path = self.project_root / "config" / "knowledge_services" / "sources.yaml"
        self._sources: dict[str, KnowledgeSource] | None = None

    def load(self) -> list[KnowledgeSource]:
        if not self.path.is_file():
            raise ConfigError(f"Knowledge Source配置不存在: {self.path}")
        try:
            raw = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        except Exception as exc:
            raise ConfigError(f"Knowledge Source配置读取失败: {self.path}: {exc}") from exc
        items = raw.get("sources") if isinstance(raw, dict) else None
        if not isinstance(items, list):
            raise ConfigError(f"Knowledge Source配置必须包含sources列表: {self.path}")
        sources: dict[str, KnowledgeSource] = {}
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise ConfigError(f"sources[{index}]必须是对象")
            provider = item.get("provider") or {}
            source = KnowledgeSource(
                source_id=str(item.get("source_id") or "").strip(),
                service_id=str(item.get("service_id") or "").strip(),
                provider_type=str(provider.get("type") if isinstance(provider, dict) else provider or "").strip(),
                location=str(item.get("location") or "").strip(),
                schema_type=str(item.get("schema") or "").strip(),
                status=str(item.get("status") or "active").strip(),
                version=str(item.get("version") or "1.0").strip(),
                options=dict(item.get("options") or {}),
            )
            try:
                source.validate()
            except ValueError as exc:
                raise ConfigError(str(exc)) from exc
            if source.source_id in sources:
                raise ConfigError(f"Knowledge Source重复: {source.source_id}")
            sources[source.source_id] = source
        self._sources = sources
        return list(sources.values())

    def get(self, source_id: str) -> KnowledgeSource:
        if self._sources is None:
            self.load()
        assert self._sources is not None
        try:
            return self._sources[source_id]
        except KeyError as exc:
            raise KeyError(f"Knowledge Source未注册: {source_id}") from exc

    def get_for_service(self, service_id: str) -> KnowledgeSource:
        if self._sources is None:
            self.load()
        assert self._sources is not None
        matches = [item for item in self._sources.values() if item.service_id == service_id and item.status == "active"]
        if not matches:
            raise KeyError(f"服务没有可用Knowledge Source: {service_id}")
        if len(matches) > 1:
            raise ValueError(f"M1仅支持每个服务一个活动Knowledge Source: {service_id}")
        return matches[0]
