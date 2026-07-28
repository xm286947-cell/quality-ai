from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class WorkflowNode:
    id: str
    type: str
    handler: str
    enabled: bool = True
    config: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AgentProfile:
    agent_id: str
    name: str
    version: str
    description: str
    workflow: tuple[WorkflowNode, ...]
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    plugin: dict[str, Any] = field(default_factory=dict)
    asset_dir: str = ""


@dataclass
class RuntimeRequest:
    agent_id: str
    inputs: dict[str, Any]
    request_id: str = ""
    options: dict[str, Any] = field(default_factory=dict)


@dataclass
class RuntimeContext:
    request: RuntimeRequest
    profile: AgentProfile
    data: dict[str, Any] = field(default_factory=dict)
    node_results: dict[str, Any] = field(default_factory=dict)


@dataclass
class RuntimeResult:
    request_id: str
    agent_id: str
    agent_version: str
    status: str
    output: dict[str, Any]
    trace_path: str
