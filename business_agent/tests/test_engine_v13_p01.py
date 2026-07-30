from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from business_agent.common.exceptions import (
    AgentRegistrationError,
    ConfigurationError,
    EngineLifecycleError,
)
from business_agent.engine import BusinessAgentEngine
from business_agent.models import AgentProfile
from business_agent.runtime import EngineState


class BusinessAgentEngineP01Test(unittest.TestCase):
    def test_lifecycle(self) -> None:
        engine = BusinessAgentEngine()
        self.assertEqual(engine.state, EngineState.CREATED)

        engine.initialize()
        self.assertEqual(engine.state, EngineState.INITIALIZED)
        self.assertTrue(engine.health()["ready"])

        engine.start()
        self.assertEqual(engine.state, EngineState.RUNNING)

        engine.stop()
        self.assertEqual(engine.state, EngineState.STOPPED)

    def test_invalid_transition(self) -> None:
        with self.assertRaises(EngineLifecycleError):
            BusinessAgentEngine().start()

    def test_agent_registry(self) -> None:
        profile = AgentProfile(
            agent_id="repeat_case",
            name="Repeat Case",
            version="1.0",
            description="test",
            workflow=(),
        )
        engine = BusinessAgentEngine().initialize(profiles=(profile,))
        self.assertEqual(engine.registry.resolve("repeat_case"), profile)

        with self.assertRaises(AgentRegistrationError):
            engine.registry.register(profile)

    def test_json_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "engine.json"
            config_path.write_text(
                json.dumps(
                    {
                        "log_level": "DEBUG",
                        "strict_agent_registration": False,
                        "metadata": {"environment": "test"},
                    }
                ),
                encoding="utf-8",
            )
            engine = BusinessAgentEngine().initialize(config_path)
            self.assertEqual(engine.configuration.log_level, "DEBUG")
            self.assertFalse(engine.configuration.strict_agent_registration)

    def test_missing_configuration(self) -> None:
        with self.assertRaises(ConfigurationError):
            BusinessAgentEngine().initialize("/not/exist/config.json")


if __name__ == "__main__":
    unittest.main()
