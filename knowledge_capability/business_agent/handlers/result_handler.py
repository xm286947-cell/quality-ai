from __future__ import annotations

from business_agent.contracts.execution import ExecutionContext
from business_agent.handlers.base import ExecutionHandler


class ResultHandler(ExecutionHandler):
    name = "result"

    def handle(self, context: ExecutionContext) -> ExecutionContext:
        if context.model_result.get("status") != "completed":
            raise ValueError("Model result must be completed before result building")
        knowledge_result = context.knowledge.get("result") or {}
        evidence = list(context.knowledge.get("evidence") or [])
        candidates = self._extract_candidates(knowledge_result)
        context.result = {
            "accepted": True,
            "agent_id": context.agent_id,
            "analysis": context.model_result.get("text", ""),
            "query": context.input.get("text") or context.input.get("query") or "",
            "knowledge": {
                "status": context.knowledge.get("status", "unknown"),
                "result": knowledge_result,
                "candidate_count": len(candidates),
                "candidates": candidates,
                "evidence": evidence,
            },
            "model": {
                "provider": context.model_result.get("provider"),
                "name": context.model_result.get("model"),
                "finish_reason": context.model_result.get("finish_reason"),
                "usage": context.model_result.get("usage") or {},
            },
        }
        return context

    @staticmethod
    def _extract_candidates(result: object) -> list[object]:
        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            for key in ("items", "results", "candidates", "matches"):
                value = result.get(key)
                if isinstance(value, list):
                    return value
        return []
