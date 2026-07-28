from __future__ import annotations

from typing import Any

from business_agent.contracts.execution import ExecutionContext
from business_agent.handlers.base import ExecutionHandler
from business_agent.knowledge import KnowledgeClientError, KnowledgeHttpClient


class KnowledgeHandler(ExecutionHandler):
    """Build and execute the Knowledge Contract request over HTTP."""

    name = "knowledge"

    def __init__(self, client: KnowledgeHttpClient | None = None) -> None:
        self.client = client or KnowledgeHttpClient()

    def handle(self, context: ExecutionContext) -> ExecutionContext:
        options = dict(context.variables.get("options") or {})
        knowledge_options = dict(options.get("knowledge") or {})
        enabled = knowledge_options.get("enabled", True)
        if not enabled:
            context.knowledge = {"status": "skipped", "reason": "disabled_by_execution_options"}
            return context

        payload = self._build_request(context, knowledge_options)
        try:
            response = self.client.query(payload)
        except KnowledgeClientError as exc:
            # Raise a structured runtime error; ExecutionRuntime converts it to EXECUTION_STEP_FAILED.
            error = RuntimeError(f"{exc.code}: {exc.message}")
            error.knowledge_error = exc  # type: ignore[attr-defined]
            raise error from exc

        context.knowledge = {
            "status": "success" if response.get("success") else "failed",
            "request": payload,
            "response": response,
            "result": response.get("result") or {},
            "evidence": response.get("evidence") or [],
            "trace": response.get("trace") or [],
            "warnings": response.get("warnings") or [],
        }
        if context.knowledge["warnings"]:
            context.variables.setdefault("warnings", []).extend(context.knowledge["warnings"])
        return context

    @staticmethod
    def _build_request(context: ExecutionContext, knowledge_options: dict[str, Any]) -> dict[str, Any]:
        query_text = str(
            knowledge_options.get("query_text")
            or context.input.get("text")
            or context.input.get("query")
            or ""
        ).strip()
        if not query_text:
            raise ValueError("Knowledge query text is required in input.text or options.knowledge.query_text")

        caller = dict(context.variables.get("caller") or {})
        caller.setdefault("type", "business_agent")
        caller.setdefault("agent_id", context.agent_id)

        return {
            "contract_version": "V1.0",
            "request_id": context.request_id,
            "service_id": str(knowledge_options.get("service_id") or "repeat_case_service"),
            "query": {"text": query_text},
            "filters": dict(knowledge_options.get("filters") or {}),
            "requested_fields": list(knowledge_options.get("requested_fields") or []),
            "options": {
                "top_k": int(knowledge_options.get("top_k", 5)),
                **dict(knowledge_options.get("query_options") or {}),
            },
            "caller": caller,
        }
