from .context import RuntimeContext
from .errors import KnowledgeRuntimeError
from .result_mapper import ResultMapper
from .service_catalog import ServiceCatalogEntry, ServiceCatalogLoader
from .trace import TraceManager
from .validation import ValidationIssue, ValidationReport, validate_runtime_configuration


def build_runtime(project_root):
    # Lazy import avoids framework/runtime package initialization cycle.
    from .bootstrap import build_runtime as _build_runtime

    return _build_runtime(project_root)


__all__ = [
    "build_runtime",
    "RuntimeContext",
    "KnowledgeRuntimeError",
    "ResultMapper",
    "ServiceCatalogEntry",
    "ServiceCatalogLoader",
    "TraceManager",
    "ValidationIssue",
    "ValidationReport",
    "validate_runtime_configuration",
]
