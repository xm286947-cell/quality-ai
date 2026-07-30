class BusinessAgentError(Exception):
    """Base exception for Business Agent Engine failures."""


class ConfigurationError(BusinessAgentError):
    """Raised when runtime configuration is invalid or unavailable."""


class EngineLifecycleError(BusinessAgentError):
    """Raised when an invalid engine lifecycle transition is requested."""


class AgentRegistrationError(BusinessAgentError):
    """Raised when an agent cannot be registered or resolved."""
