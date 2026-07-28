class BusinessAgentError(RuntimeError):
    """Base error for BUSINESS_AGENT_ENGINE runtime."""


class AgentProfileError(BusinessAgentError):
    """Raised when an Agent Profile is invalid."""


class WorkflowExecutionError(BusinessAgentError):
    """Raised when a workflow node cannot be executed."""
