from __future__ import annotations

from pathlib import Path
from typing import Any

from business_agent.models import RuntimeContext, WorkflowNode
from .client import KnowledgeClient
from .models import KnowledgeRequest


class KnowledgeContractAdapter:
    """Business-neutral workflow adapter for QUALITY_AGENT_CONTRACT V1.0."""

    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root).resolve()

    def search(self, context: RuntimeContext, node: WorkflowNode) -> dict[str, Any]:
        options = {**node.config, **context.request.options.get("knowledge", {})}
        inputs = context.request.inputs
        cases = list(context.data.get("cases") or [])
        if not cases:
            raise ValueError("INVALID_INPUT: context.cases is empty; parse_input must run before knowledge_search")
        enabled = bool(options.get("enabled", True))
        if not enabled:
            payload = {"status": "SKIPPED", "items": [], "total": 0, "provider": "disabled", "case_results": []}
            return {"summary": payload, "output": payload, "context_updates": {"knowledge_response": payload}}

        request_options = dict(options.get("request_options") or {})
        request_options.setdefault("top_k", int(inputs.get("top_k") or options.get("top_k") or 10))
        client = KnowledgeClient(self.project_root, options)
        case_results: list[dict[str, Any]] = []
        total_items = 0
        total_evidence = 0
        total_elapsed = 0
        for index, case in enumerate(cases, start=1):
            query_text = str(case.get("query_text") or "").strip()
            case_id = str(case.get("case_id") or f"CASE-{index:04d}")
            if not query_text:
                raise ValueError(f"INVALID_INPUT: empty query_text for case {case_id}")
            request = KnowledgeRequest(
                request_id=f"{context.request.request_id}:{case_id}",
                service_id=str(options.get("service_id") or "repeat_case_service"),
                query={"text": query_text},
                filters=dict(options.get("filters") or {}),
                requested_fields=list(options.get("requested_fields") or []),
                options=request_options,
                caller={
                    "type": "business_agent",
                    "agent_id": context.profile.agent_id,
                    "agent_version": context.profile.version,
                },
            )
            response = client.search(request)
            payload = response.to_dict()
            evidence_count = sum(len(item.evidence) for item in response.items)
            total_items += len(response.items)
            total_evidence += evidence_count
            total_elapsed += response.elapsed_ms
            case_results.append({
                "case_id": case_id,
                "query_text": query_text,
                "request": request.to_dict(),
                "response": payload,
                "recall_count": len(response.items),
                "evidence_count": evidence_count,
            })

        aggregate = {
            "status": "SUCCESS",
            "provider": case_results[0]["response"].get("provider", "") if case_results else "",
            "case_count": len(case_results),
            "total": total_items,
            "elapsed_ms": total_elapsed,
            "items": [
                {"case_id": item["case_id"], "items": item["response"].get("items", [])}
                for item in case_results
            ],
            "case_results": case_results,
        }
        summary = {
            "status": "SUCCESS",
            "case_count": len(case_results),
            "recall_count": total_items,
            "evidence_count": total_evidence,
            "elapsed_ms": total_elapsed,
        }
        return {
            "summary": summary,
            "output": aggregate,
            "context_updates": {
                "knowledge_request": case_results[0]["request"] if len(case_results) == 1 else {},
                "knowledge_requests": [item["request"] for item in case_results],
                "knowledge_response": aggregate,
                "knowledge_case_results": case_results,
                "knowledge_items": aggregate["items"],
            },
        }

    @staticmethod
    def _resolve_query(inputs: dict[str, Any], options: dict[str, Any]) -> str:
        for key in ("knowledge_query", "query", "problem_description", "description", "title", "query_id"):
            value = inputs.get(key)
            if value:
                return str(value)
        return str(options.get("default_query") or "")
