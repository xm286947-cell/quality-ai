from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .container import DependencyContainer
from .knowledge import KnowledgeGateway
from .registry import CapabilityRegistry
from .service_locator import ServiceLocator


@dataclass
class RuntimeCapabilityBinding:
    registry: CapabilityRegistry
    container: DependencyContainer
    locator: ServiceLocator

    @classmethod
    def create_default(cls, *, knowledge_client: Any | None = None) -> "RuntimeCapabilityBinding":
        registry = CapabilityRegistry()
        container = DependencyContainer()
        locator = ServiceLocator()
        if knowledge_client is not None:
            container.register_instance("knowledge_client", knowledge_client)
            registry.register(
                "knowledge",
                lambda: KnowledgeGateway(container.resolve("knowledge_client")),
            )
        return cls(registry=registry, container=container, locator=locator)

    def attach(self, context: Any) -> None:
        bindings = self.locator.load_profile_bindings(context.profile)
        data = getattr(context, "data", None)
        if not isinstance(data, dict):
            raise TypeError("runtime context must expose mutable data")
        data["capability_bindings"] = bindings
        data.setdefault("capabilities", {})

    def invoke(
        self,
        context: Any,
        capability_type: str,
        binding_name: str,
        payload: dict[str, Any] | None = None,
    ):
        bindings = context.data.get("capability_bindings")
        if bindings is None:
            self.attach(context)
            bindings = context.data["capability_bindings"]
        binding = self.locator.resolve(bindings, capability_type, binding_name)
        factory = self.registry.resolve(capability_type)
        gateway = factory()
        return gateway.invoke(binding, context=context, payload=payload)
