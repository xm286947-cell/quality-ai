"""Knowledge Capability platform foundation (Design V1.1, M1 Iteration-01)."""

from .framework.runtime import KnowledgeCapabilityRuntime
from .runtime.bootstrap import build_runtime

__all__ = ["KnowledgeCapabilityRuntime", "build_runtime"]
