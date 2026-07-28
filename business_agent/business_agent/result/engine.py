from __future__ import annotations

from typing import Any


class ResultEngine:
    """Normalize workflow output to a stable platform result object."""

    def normalize(self, output: Any, node_results: dict[str, Any]) -> dict[str, Any]:
        if output is None:
            return {"node_results": node_results}
        if not isinstance(output, dict):
            return {"value": output}
        return output
