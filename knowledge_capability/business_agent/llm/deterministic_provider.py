from __future__ import annotations

from .provider import LLMProvider, ModelInvocation, ModelOutput


class DeterministicLLMProvider(LLMProvider):
    """Offline provider used as the default runtime baseline and in regression tests."""

    def invoke(self, invocation: ModelInvocation) -> ModelOutput:
        metadata = invocation.metadata
        query = str(metadata.get("query") or "").strip()
        items = list(metadata.get("knowledge_items") or [])
        evidence = list(metadata.get("evidence") or [])
        if items:
            first = items[0] if isinstance(items[0], dict) else {"value": items[0]}
            case_id = first.get("case_id") or first.get("id") or first.get("knowledge_id") or "unknown"
            score = first.get("score")
            score_text = f"，相似度 {score}" if score is not None else ""
            text = f"已完成重复问题分析。输入：{query}。检索到 {len(items)} 条候选，首要候选为 {case_id}{score_text}。"
        else:
            text = f"已完成重复问题分析。输入：{query}。未检索到可用历史候选。"
        if evidence:
            text += f" 已关联 {len(evidence)} 条证据。"
        return ModelOutput(
            text=text,
            model="deterministic-repeat-case-v1",
            provider="builtin",
            usage={"prompt_tokens": len(invocation.prompt.split()), "completion_tokens": len(text.split())},
            raw={"offline": True},
        )
