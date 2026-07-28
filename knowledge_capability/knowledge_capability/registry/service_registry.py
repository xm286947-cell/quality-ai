from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from knowledge_capability.contracts import KnowledgeRequest, KnowledgeResponse


class KnowledgeServiceHandler(Protocol):
    def handle(self, request: KnowledgeRequest) -> KnowledgeResponse: ...


@dataclass(frozen=True)
class ServiceRegistration:
    service_id: str
    version: str
    status: str
    profile_name: str
    handler: KnowledgeServiceHandler


class ServiceRegistry:
    """In-process registry for M1. Future implementations may use remote discovery."""

    def __init__(self) -> None:
        self._services: dict[str, ServiceRegistration] = {}

    def register(self, registration: ServiceRegistration, *, replace: bool = False) -> None:
        key = registration.service_id.strip()
        if not key:
            raise ValueError("service_id不能为空")
        if key in self._services and not replace:
            raise ValueError(f"服务已注册: {key}")
        self._services[key] = registration

    def get(self, service_id: str) -> ServiceRegistration:
        try:
            return self._services[service_id]
        except KeyError as exc:
            raise KeyError(f"服务未注册: {service_id}") from exc

    def list(self, *, status: str | None = None) -> list[ServiceRegistration]:
        values = list(self._services.values())
        if status is not None:
            values = [item for item in values if item.status == status]
        return sorted(values, key=lambda item: item.service_id)
