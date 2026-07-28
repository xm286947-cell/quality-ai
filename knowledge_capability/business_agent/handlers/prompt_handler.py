from __future__ import annotations

import json
from typing import Any

from business_agent.contracts.execution import ExecutionContext
from business_agent.handlers.base import ExecutionHandler


class PromptHandler(ExecutionHandler):
    name = "prompt"

    def handle(self, context: ExecutionContext) -> ExecutionContext:
        query = str(context.input.get("text") or context.input.get("query") or "").strip()
        knowledge_result = context.knowledge.get("result") or {}
        evidence = context.knowledge.get("evidence") or []
        items = self._extract_items(knowledge_result)
        system_prompt = (
            "你是重复问题分析业务智能体。只基于输入问题、知识检索结果和证据形成结论；"
            "没有知识命中时必须明确说明，不得虚构历史案例。"
        )
        user_prompt = "\n".join(
            [
                f"当前问题：{query}",
                f"候选知识：{json.dumps(items, ensure_ascii=False, default=str)}",
                f"证据：{json.dumps(evidence, ensure_ascii=False, default=str)}",
                "请输出简洁的重复问题分析结果。",
            ]
        )
        context.prompt = {
            "status": "built",
            "template_id": "repeat_case_analysis_v1",
            "system": system_prompt,
            "user": user_prompt,
            "variables": {
                "query": query,
                "knowledge_items": items,
                "evidence": evidence,
            },
        }
        return context

    @staticmethod
    def _extract_items(result: Any) -> list[Any]:
        if isinstance(result, list):
            return result
        if not isinstance(result, dict):
            return []
        for key in ("items", "results", "candidates", "matches"):
            value = result.get(key)
            if isinstance(value, list):
                return value
        return []
