from __future__ import annotations

from collections.abc import Callable
from threading import RLock
from typing import Any

from .errors import CapabilityNotFoundError, CapabilityValidationError


class DependencyContainer:
    """Minimal dependency-injection container with singleton and factory scopes."""

    def __init__(self) -> None:
        self._singletons: dict[str, Any] = {}
        self._factories: dict[str, Callable[["DependencyContainer"], Any]] = {}
        self._lock = RLock()

    def register_instance(self, name: str, value: Any, *, replace: bool = False) -> None:
        if not name:
            raise CapabilityValidationError("dependency name cannot be empty")
        with self._lock:
            if not replace and (name in self._singletons or name in self._factories):
                raise CapabilityValidationError(f"dependency already registered: {name}")
            self._factories.pop(name, None)
            self._singletons[name] = value

    def register_factory(
        self,
        name: str,
        factory: Callable[["DependencyContainer"], Any],
        *,
        replace: bool = False,
    ) -> None:
        if not name or not callable(factory):
            raise CapabilityValidationError("valid dependency name and factory required")
        with self._lock:
            if not replace and (name in self._singletons or name in self._factories):
                raise CapabilityValidationError(f"dependency already registered: {name}")
            self._singletons.pop(name, None)
            self._factories[name] = factory

    def resolve(self, name: str) -> Any:
        with self._lock:
            if name in self._singletons:
                return self._singletons[name]
            factory = self._factories.get(name)
        if factory is None:
            raise CapabilityNotFoundError(f"dependency not registered: {name}")
        return factory(self)

    def contains(self, name: str) -> bool:
        with self._lock:
            return name in self._singletons or name in self._factories
