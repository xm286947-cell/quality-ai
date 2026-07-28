from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any

from business_agent.errors import AgentProfileError
from business_agent.workflow.handler_registry import HandlerRegistry


class PluginLoader:
    """Load Agent plugins without adding business dependencies to Runtime."""

    def __init__(self, project_root: str | Path, registry: HandlerRegistry) -> None:
        self.project_root = Path(project_root).resolve()
        self.plugin_root = self.project_root / "plugins"
        self.registry = registry
        self._loaded: set[str] = set()

    def load(self, agent_id: str, plugin_config: dict[str, Any] | None = None) -> None:
        if agent_id in self._loaded:
            return
        config = plugin_config or {}
        plugin_dir = self.plugin_root / agent_id
        module_name = str(config.get("module") or "plugin.py")
        module_path = plugin_dir / module_name
        if not module_path.exists():
            raise AgentProfileError(f"Agent插件不存在: {module_path}")
        module = self._load_module(agent_id, module_path)
        register = getattr(module, "register", None)
        if not callable(register):
            raise AgentProfileError(f"Agent插件必须提供register(registry, project_root): {module_path}")
        register(self.registry, self.project_root)
        self._loaded.add(agent_id)

    @staticmethod
    def _load_module(agent_id: str, module_path: Path) -> ModuleType:
        spec = importlib.util.spec_from_file_location(f"business_agent_plugin_{agent_id}", module_path)
        if spec is None or spec.loader is None:
            raise AgentProfileError(f"无法加载Agent插件: {module_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
