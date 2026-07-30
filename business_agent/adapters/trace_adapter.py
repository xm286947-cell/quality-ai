from __future__ import annotations

from business_agent.contracts.trace import TraceContext


class TraceAdapter:
    """
    Convert runtime trace information
    into contract trace model.
    """

    @staticmethod
    def from_path(trace_path: str) -> TraceContext:
        return TraceContext(
            trace_id="",
            entries=[],
            metadata={
                "trace_path": trace_path
            }
        )
