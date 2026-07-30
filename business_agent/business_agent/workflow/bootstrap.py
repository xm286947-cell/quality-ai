from __future__ import annotations

from business_agent.capability.runtime_binding import RuntimeCapabilityBinding
from business_agent.workflow.capability_handler import CapabilityNodeHandler
from business_agent.workflow.handler_registry import HandlerRegistry


def register_capability_handlers(
    registry: HandlerRegistry,
    runtime_binding: RuntimeCapabilityBinding,
    *,
    overwrite: bool = False,
) -> HandlerRegistry:
    """Register the generic capability workflow handler."""

    registry.register(
        "capability.invoke",
        CapabilityNodeHandler(runtime_binding),
        overwrite=overwrite,
    )
    return registry
