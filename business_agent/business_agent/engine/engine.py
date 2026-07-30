from __future__ import annotations

from pathlib import Path
from threading import RLock

from business_agent.agent import AgentRegistry
from business_agent.common.exceptions import EngineLifecycleError
from business_agent.common.logging import configure_logging
from business_agent.config import ConfigurationLoader, EngineConfiguration
from business_agent.models import AgentProfile
from business_agent.runtime import EngineState


class BusinessAgentEngine:
    """P01 lifecycle shell for Business Agent Engine V1.3.

    P01 intentionally owns only configuration, logging, lifecycle and agent
    registration. Workflow, capability, prompt and business execution remain
    outside this phase.
    """

    VERSION = "1.3.0"

    def __init__(
        self,
        *,
        configuration_loader: ConfigurationLoader | None = None,
        registry: AgentRegistry | None = None,
    ) -> None:
        self._loader = configuration_loader or ConfigurationLoader()
        self._registry = registry or AgentRegistry()
        self._configuration: EngineConfiguration | None = None
        self._state = EngineState.CREATED
        self._lock = RLock()
        self._logger = configure_logging()

    @property
    def state(self) -> EngineState:
        return self._state

    @property
    def configuration(self) -> EngineConfiguration:
        if self._configuration is None:
            raise EngineLifecycleError("Engine has not been initialized")
        return self._configuration

    @property
    def registry(self) -> AgentRegistry:
        return self._registry

    def initialize(
        self,
        config_path: str | Path | None = None,
        *,
        profiles: tuple[AgentProfile, ...] = (),
    ) -> "BusinessAgentEngine":
        with self._lock:
            if self._state not in {EngineState.CREATED, EngineState.STOPPED}:
                raise EngineLifecycleError(
                    f"Cannot initialize engine from state: {self._state.value}"
                )

            self._configuration = self._loader.load(config_path)
            self._logger = configure_logging(self._configuration.log_level)
            self._registry.register_many(
                profiles,
                overwrite=not self._configuration.strict_agent_registration,
            )
            self._state = EngineState.INITIALIZED
            self._logger.info(
                "Business Agent Engine initialized; version=%s agents=%d",
                self.VERSION,
                len(self._registry.list_profiles()),
            )
            return self

    def start(self) -> "BusinessAgentEngine":
        with self._lock:
            if self._state != EngineState.INITIALIZED:
                raise EngineLifecycleError(
                    f"Cannot start engine from state: {self._state.value}"
                )
            self._state = EngineState.RUNNING
            self._logger.info("Business Agent Engine started")
            return self

    def stop(self) -> "BusinessAgentEngine":
        with self._lock:
            if self._state not in {EngineState.INITIALIZED, EngineState.RUNNING}:
                raise EngineLifecycleError(
                    f"Cannot stop engine from state: {self._state.value}"
                )
            self._state = EngineState.STOPPED
            self._logger.info("Business Agent Engine stopped")
            return self

    def health(self) -> dict[str, object]:
        return {
            "engine": "business_agent",
            "version": self.VERSION,
            "state": self._state.value,
            "ready": self._state in {
                EngineState.INITIALIZED,
                EngineState.RUNNING,
            },
            "registered_agents": [
                profile.agent_id for profile in self._registry.list_profiles()
            ],
        }
