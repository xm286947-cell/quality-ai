from __future__ import annotations

from business_agent.handlers import ContextHandler, KnowledgeHandler, LLMHandler, PromptHandler, ResultHandler

from .agent_definition import AgentDefinition


class AgentRegistry:
    """In-memory runtime registry used to resolve an agent execution pipeline."""

    def __init__(self) -> None:
        self._definitions: dict[str, AgentDefinition] = {}

    def register(self, definition: AgentDefinition, *, replace: bool = False) -> None:
        if definition.agent_id in self._definitions and not replace:
            raise ValueError(f"agent already registered: {definition.agent_id}")
        self._definitions[definition.agent_id] = definition

    def get(self, agent_id: str) -> AgentDefinition | None:
        return self._definitions.get(agent_id)

    def list(self) -> tuple[AgentDefinition, ...]:
        return tuple(self._definitions[key] for key in sorted(self._definitions))

    @classmethod
    def default(cls) -> "AgentRegistry":
        registry = cls()
        registry.register(
            AgentDefinition.create(
                "repeat_case_agent",
                [
                    ContextHandler(),
                    KnowledgeHandler(),
                    PromptHandler(),
                    LLMHandler(),
                    ResultHandler(),
                ],
                description="Repeat Case Business Agent",
            )
        )
        return registry
