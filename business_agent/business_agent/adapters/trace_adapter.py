from __future__ import annotations

from pathlib import Path

from business_agent.contracts.trace import TraceContext


class TraceAdapter:
    """Create the public trace contract from the current file-based trace."""

    @staticmethod
    def from_path(trace_path: str, *, request_id: str = "") -> TraceContext:
        normalized_path = str(Path(trace_path)) if trace_path else ""
        return TraceContext(
            trace_id="",
            request_id=request_id,
            entries=[],
            debug={"trace_path": normalized_path} if normalized_path else {},
        )
