from __future__ import annotations

from threading import RLock
from typing import Iterable

from business_agent.common.exceptions import AgentRegistrationError
from business_agent.models import AgentProfile


class AgentRegistry:
    """Thread-safe registry for immutable AgentProfile objects."""

    def __init__(self) -> None:
        self._profiles: dict[str, AgentProfile] = {}
        self._lock = RLock()

    def register(self, profile: AgentProfile, *, overwrite: bool = False) -> None:
        if not profile.agent_id.strip():
            raise AgentRegistrationError("agent_id must not be empty")

        with self._lock:
            if profile.agent_id in self._profiles and not overwrite:
                raise AgentRegistrationError(
                    f"Agent already registered: {profile.agent_id}"
                )
            self._profiles[profile.agent_id] = profile

    def resolve(self, agent_id: str) -> AgentProfile:
        with self._lock:
            try:
                return self._profiles[agent_id]
            except KeyError as exc:
                raise AgentRegistrationError(
                    f"Agent is not registered: {agent_id}"
                ) from exc

    def list_profiles(self) -> tuple[AgentProfile, ...]:
        with self._lock:
            return tuple(
                self._profiles[key] for key in sorted(self._profiles)
            )

    def register_many(
        self,
        profiles: Iterable[AgentProfile],
        *,
        overwrite: bool = False,
    ) -> None:
        for profile in profiles:
            self.register(profile, overwrite=overwrite)
