from __future__ import annotations

from business_agent.contracts.execution import ExecutionContext
from business_agent.handlers.base import ExecutionHandler
from business_agent.llm import DeterministicLLMProvider, LLMProvider, ModelInvocation


class LLMHandler(ExecutionHandler):
    name = "llm"

    def __init__(self, provider: LLMProvider | None = None) -> None:
        self.provider = provider or DeterministicLLMProvider()

    def handle(self, context: ExecutionContext) -> ExecutionContext:
        if context.prompt.get("status") != "built":
            raise ValueError("Prompt must be built before model invocation")
        variables = dict(context.prompt.get("variables") or {})
        output = self.provider.invoke(
            ModelInvocation(
                system_prompt=str(context.prompt.get("system") or ""),
                prompt=str(context.prompt.get("user") or ""),
                metadata=variables,
            )
        )
        context.model_result = {
            "status": "completed",
            "text": output.text,
            "provider": output.provider,
            "model": output.model,
            "finish_reason": output.finish_reason,
            "usage": output.usage,
            "raw": output.raw,
        }
        return context
