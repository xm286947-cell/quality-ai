from __future__ import annotations

from pathlib import Path

from knowledge_capability.contracts import KnowledgeRequest
from knowledge_capability.runtime import build_runtime
from knowledge_capability.runtime.validation import validate_runtime_configuration


def test_i08_delivery_configuration_is_valid():
    root = Path(__file__).resolve().parents[1]
    report = validate_runtime_configuration(root)
    assert report.valid, report.to_dict()
    assert "repeat_case_service" in report.services


def test_i08_runtime_maps_unknown_service_without_unhandled_exception():
    root = Path(__file__).resolve().parents[1]
    response = build_runtime(root).execute(
        KnowledgeRequest(service_id="missing_service", query={"text": "test"})
    )
    assert not response.success
    assert response.error is not None
    assert response.error.code == "SERVICE_NOT_FOUND"
