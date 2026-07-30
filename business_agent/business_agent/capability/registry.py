from __future__ import annotations

from collections.abc import Callable
from threading import RLock
from typing import Any

from .errors import CapabilityNotFoundError, CapabilityValidationError

GatewayFactory = Callable[..., Any]


class CapabilityRegistry:
    """Thread-safe registry for capability gateway factories."""

    def __init__(self) -> None:
        self._factories: dict[str, GatewayFactory] = {}
        self._lock = RLock()

    def register(
        self,
        capability_type: str,
        factory: GatewayFactory,
        *,
        replace: bool = False,
    ) -> None:
        key = capability_type.strip().lower()
        if not key:
            raise CapabilityValidationError("capability_type cannot be empty")
        if not callable(factory):
            raise CapabilityValidationError("gateway factory must be callable")
        with self._lock:
            if key in self._factories and not replace:
                raise CapabilityValidationError(
                    f"capability gateway already registered: {key}"
                )
            self._factories[key] = factory

    def unregister(self, capability_type: str) -> None:
        with self._lock:
            self._factories.pop(capability_type.strip().lower(), None)

    def resolve(self, capability_type: str) -> GatewayFactory:
        key = capability_type.strip().lower()
        with self._lock:
            try:
                return self._factories[key]
            except KeyError as exc:
                raise CapabilityNotFoundError(
                    f"capability gateway not registered: {key}"
                ) from exc

    def contains(self, capability_type: str) -> bool:
        with self._lock:
            return capability_type.strip().lower() in self._factories

    def list_types(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(sorted(self._factories))
