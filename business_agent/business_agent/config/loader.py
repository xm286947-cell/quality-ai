from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from business_agent.common.exceptions import ConfigurationError


@dataclass(frozen=True)
class EngineConfiguration:
    log_level: str = "INFO"
    strict_agent_registration: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


class ConfigurationLoader:
    """Load P01 engine configuration from JSON or environment variables."""

    ENV_PREFIX = "BUSINESS_AGENT_"

    def load(self, path: str | Path | None = None) -> EngineConfiguration:
        payload: dict[str, Any] = {}

        if path:
            config_path = Path(path)
            if not config_path.exists():
                raise ConfigurationError(f"Configuration file not found: {config_path}")
            if config_path.suffix.lower() != ".json":
                raise ConfigurationError(
                    "P01 standard-library loader supports JSON configuration only"
                )
            try:
                payload = json.loads(config_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise ConfigurationError(
                    f"Failed to load configuration: {config_path}"
                ) from exc

        log_level = os.getenv(
            f"{self.ENV_PREFIX}LOG_LEVEL",
            str(payload.get("log_level", "INFO")),
        )
        strict_value = os.getenv(
            f"{self.ENV_PREFIX}STRICT_AGENT_REGISTRATION",
            str(payload.get("strict_agent_registration", True)),
        )
        strict = str(strict_value).strip().lower() not in {"0", "false", "no", "off"}

        metadata = payload.get("metadata", {})
        if not isinstance(metadata, dict):
            raise ConfigurationError("metadata must be an object")

        return EngineConfiguration(
            log_level=log_level,
            strict_agent_registration=strict,
            metadata=dict(metadata),
        )
