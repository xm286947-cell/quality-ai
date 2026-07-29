"""Backward-compatible imports for API contract models.

New code should import from :mod:`business_agent.contracts`.
"""
from business_agent.contracts.api import (
    AgentListResponse,
    AgentSummary,
    ErrorBody,
    ErrorResponse,
    ExecutionResponse,
    HealthResponse,
)

__all__ = [
    "AgentListResponse", "AgentSummary", "ErrorBody", "ErrorResponse", "ExecutionResponse", "HealthResponse"
]
