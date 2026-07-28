from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from knowledge_capability.profiles import ServiceProfileLoader
from knowledge_capability.runtime.service_catalog import ServiceCatalogLoader


@dataclass
class ValidationIssue:
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationReport:
    valid: bool
    services: list[str] = field(default_factory=list)
    issues: list[ValidationIssue] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "services": self.services,
            "issues": [
                {"code": issue.code, "message": issue.message, "details": issue.details}
                for issue in self.issues
            ],
        }


def validate_runtime_configuration(project_root: str | Path) -> ValidationReport:
    root = Path(project_root).resolve()
    issues: list[ValidationIssue] = []
    services: list[str] = []

    try:
        catalog = ServiceCatalogLoader(root).load()
    except Exception as exc:
        return ValidationReport(
            valid=False,
            issues=[ValidationIssue("CATALOG_ERROR", str(exc), {"error_type": type(exc).__name__})],
        )

    profile_loader = ServiceProfileLoader(root)
    seen: set[str] = set()
    for entry in catalog:
        services.append(entry.service_id)
        if entry.service_id in seen:
            issues.append(ValidationIssue("DUPLICATE_SERVICE", f"重复服务: {entry.service_id}"))
        seen.add(entry.service_id)
        try:
            profile = profile_loader.load(entry.profile_name)
            if profile.service_id != entry.service_id:
                issues.append(
                    ValidationIssue(
                        "SERVICE_PROFILE_MISMATCH",
                        f"Registry与Profile的service_id不一致: {entry.service_id} != {profile.service_id}",
                        {"service_id": entry.service_id, "profile_name": entry.profile_name},
                    )
                )
            if entry.status not in {"active", "disabled"}:
                issues.append(
                    ValidationIssue(
                        "INVALID_SERVICE_STATUS",
                        f"不支持的服务状态: {entry.status}",
                        {"service_id": entry.service_id},
                    )
                )
        except Exception as exc:
            issues.append(
                ValidationIssue(
                    "PROFILE_ERROR",
                    str(exc),
                    {"service_id": entry.service_id, "profile_name": entry.profile_name, "error_type": type(exc).__name__},
                )
            )

    return ValidationReport(valid=not issues, services=services, issues=issues)
