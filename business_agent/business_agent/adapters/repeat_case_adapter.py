from __future__ import annotations

from pathlib import Path
from typing import Any

from builder.analysis_pipeline_runner import run_analysis_pipeline
from business_agent.models import RuntimeContext, WorkflowNode


class RepeatCaseAdapter:
    """Migration adapter: expose the existing REPEAT_CASE pipeline as a platform handler."""

    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root).resolve()

    def run_analysis(self, context: RuntimeContext, node: WorkflowNode) -> dict[str, Any]:
        inputs = context.request.inputs
        options = {**node.config, **context.request.options}
        result = run_analysis_pipeline(
            self.project_root,
            input_path=inputs.get("input"),
            query_id=inputs.get("query_id"),
            from_stage=str(inputs.get("from_stage") or options.get("from_stage") or "parse"),
            top_k=inputs.get("top_k", options.get("top_k")),
            overwrite=bool(inputs.get("overwrite", options.get("overwrite", False))),
            mock=bool(inputs.get("mock", options.get("mock", False))),
            skip_ai=bool(inputs.get("skip_ai", options.get("skip_ai", False))),
        )
        success = bool(result.get("success", False))
        knowledge_response = context.data.get("knowledge_response") or {}
        parsed_cases = context.data.get("cases") or []
        # Keep the original pipeline unchanged. Contract results are attached as
        # platform context for integration verification and later retrieval replacement.
        platform_context = result.setdefault("platform_context", {})
        if parsed_cases:
            platform_context["cases"] = parsed_cases
        if knowledge_response:
            platform_context["knowledge"] = knowledge_response
        return {
            "summary": {
                "success": success,
                "query_count": len(result.get("queries") or []),
                "knowledge_status": knowledge_response.get("status", "NOT_CALLED"),
                "knowledge_recall_count": len(knowledge_response.get("items") or []),
            },
            "output": result,
            "context_updates": {"repeat_case_result": result},
        }
