from __future__ import annotations

from pathlib import Path

from knowledge_capability.runtime.validation import validate_runtime_configuration


def test_runtime_configuration_is_valid_for_delivery_package():
    root = Path(__file__).resolve().parents[1]
    report = validate_runtime_configuration(root)
    assert report.valid, report.to_dict()
    assert "repeat_case_service" in report.services
