class CapabilityError(RuntimeError):
    """Base error for capability integration."""


class CapabilityNotFoundError(CapabilityError):
    """Raised when a capability or service binding cannot be resolved."""


class CapabilityValidationError(CapabilityError):
    """Raised when binding, request, or response validation fails."""


class CapabilityInvocationError(CapabilityError):
    """Raised when an external capability invocation fails."""

    def __init__(self, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.retryable = retryable
