from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import yaml

from business_agent.errors import AgentProfileError
from business_agent.models import AgentProfile, WorkflowNode


class AgentProfileLoader:
    """Load both standard plugin profiles and legacy config profiles."""

    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root).resolve()
        self.profile_dir = self.project_root / "config" / "agents"
        self.plugin_dir = self.project_root / "plugins"

    def load(self, agent_id: str) -> AgentProfile:
        normalized = str(agent_id).strip()
        if not normalized or Path(normalized).name != normalized:
            raise AgentProfileError(f"非法Agent ID: {agent_id}")
        plugin_profile = self.plugin_dir / normalized / "agent.yaml"
        legacy_profile = self.profile_dir / f"{normalized}.yaml"
        path = plugin_profile if plugin_profile.exists() else legacy_profile
        if not path.exists():
            raise AgentProfileError(f"Agent Profile不存在: {normalized}")
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            raise AgentProfileError(f"Agent Profile读取失败: {path}: {exc}") from exc
        if not isinstance(raw, Mapping):
            raise AgentProfileError(f"Agent Profile根节点必须是对象: {path}")
        return self._build(dict(raw), path)

    def list_profiles(self) -> list[dict[str, Any]]:
        ids = {p.stem for p in self.profile_dir.glob("*.yaml")} if self.profile_dir.exists() else set()
        if self.plugin_dir.exists():
            ids.update(p.parent.name for p in self.plugin_dir.glob("*/agent.yaml"))
        return [{"agent_id": p.agent_id, "name": p.name, "version": p.version, "description": p.description} for p in (self.load(x) for x in sorted(ids))]

    def _build(self, raw: dict[str, Any], path: Path) -> AgentProfile:
        agent = raw.get("agent") or {}
        asset_dir = path.parent
        workflow = raw.get("workflow") or self._load_yaml_asset(asset_dir, raw.get("workflow_file")) or {}
        nodes_raw = workflow.get("nodes") or []
        if not isinstance(agent, Mapping) or not isinstance(nodes_raw, list) or not nodes_raw:
            raise AgentProfileError(f"Agent或workflow.nodes无效: {path}")
        agent_id = str(agent.get("id") or (path.parent.name if path.name == "agent.yaml" else path.stem)).strip()
        expected = path.parent.name if path.name == "agent.yaml" else path.stem
        if agent_id != expected:
            raise AgentProfileError(f"Agent ID必须与目录/文件名一致: {agent_id} != {expected}")
        nodes, seen = [], set()
        for item in nodes_raw:
            if not isinstance(item, Mapping):
                raise AgentProfileError(f"workflow node必须是对象: {path}")
            node_id, handler = str(item.get("id") or "").strip(), str(item.get("handler") or "").strip()
            if not node_id or not handler or node_id in seen:
                raise AgentProfileError(f"workflow node无效或重复: {node_id}")
            seen.add(node_id)
            nodes.append(WorkflowNode(node_id, str(item.get("type") or "python_handler"), handler, bool(item.get("enabled", True)), dict(item.get("config") or {})))
        return AgentProfile(
            agent_id=agent_id, name=str(agent.get("name") or agent_id), version=str(agent.get("version") or "1.0"),
            description=str(agent.get("description") or ""), workflow=tuple(nodes),
            input_schema=self._load_json_asset(asset_dir, raw.get("input_schema_file")) or dict(raw.get("input_schema") or {}),
            output_schema=self._load_json_asset(asset_dir, raw.get("output_schema_file")) or dict(raw.get("output_schema") or {}),
            metadata=dict(raw.get("metadata") or {}), plugin=dict(raw.get("plugin") or {}), asset_dir=str(asset_dir),
        )

    @staticmethod
    def _load_yaml_asset(asset_dir: Path, name: Any) -> dict[str, Any]:
        if not name: return {}
        value = yaml.safe_load((asset_dir / str(name)).read_text(encoding="utf-8")) or {}
        if not isinstance(value, Mapping): raise AgentProfileError(f"YAML资产根节点必须是对象: {name}")
        return dict(value)

    @staticmethod
    def _load_json_asset(asset_dir: Path, name: Any) -> dict[str, Any]:
        if not name: return {}
        value = json.loads((asset_dir / str(name)).read_text(encoding="utf-8"))
        if not isinstance(value, Mapping): raise AgentProfileError(f"JSON资产根节点必须是对象: {name}")
        return dict(value)
