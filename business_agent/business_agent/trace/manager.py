from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from business_agent.models import RuntimeRequest, WorkflowNode


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class TraceManager:
    def __init__(self, project_root: str | Path, request: RuntimeRequest) -> None:
        root = Path(project_root).resolve()
        self.path = root / "output" / "agent_runs" / request.request_id / "trace.json"
        self.started = time.perf_counter()
        self.trace: dict[str, Any] = {
            "request_id": request.request_id,
            "agent_id": request.agent_id,
            "status": "RUNNING",
            "started_at": _now(),
            "completed_at": "",
            "elapsed_seconds": 0.0,
            "nodes": [],
        }

    def node_started(self, node: WorkflowNode) -> None:
        self.trace["nodes"].append({"id": node.id, "handler": node.handler, "status": "RUNNING", "started_at": _now()})
        self._write()

    def node_succeeded(self, node: WorkflowNode, result: dict[str, Any]) -> None:
        item = self.trace["nodes"][-1]
        item.update({"status": "SUCCESS", "completed_at": _now(), "summary": result.get("summary", {})})
        self._write()

    def node_failed(self, node: WorkflowNode, exc: Exception) -> None:
        item = self.trace["nodes"][-1]
        item.update({"status": "FAILED", "completed_at": _now(), "error_type": type(exc).__name__, "error": str(exc)})
        self._write()

    def node_skipped(self, node: WorkflowNode) -> None:
        self.trace["nodes"].append({"id": node.id, "handler": node.handler, "status": "SKIPPED", "completed_at": _now()})
        self._write()

    def complete(self, status: str, error: Exception | None = None) -> str:
        self.trace["status"] = status
        self.trace["completed_at"] = _now()
        self.trace["elapsed_seconds"] = round(time.perf_counter() - self.started, 3)
        if error is not None:
            self.trace["error_type"] = type(error).__name__
            self.trace["error"] = str(error)
        self._write()
        return str(self.path)

    def _write(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.trace, ensure_ascii=False, indent=2), encoding="utf-8")
