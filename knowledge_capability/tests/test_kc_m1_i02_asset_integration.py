from pathlib import Path

import pytest

from common.config_loader import ConfigError
from knowledge_capability.contracts import KnowledgeRequest
from knowledge_capability.profiles import ServiceProfileLoader
from knowledge_capability.runtime import ServiceCatalogLoader, build_runtime

ROOT = Path(__file__).resolve().parents[1]


def test_service_catalog_and_profile_are_aligned():
    entries = ServiceCatalogLoader(ROOT).load()
    assert [item.service_id for item in entries] == ["repeat_case_service"]
    profile = ServiceProfileLoader(ROOT).load(entries[0].profile_name)
    assert profile.service_id == entries[0].service_id
    assert profile.service_type == "repeat_case"
    assert profile.adapter["type"] == "existing_case_retriever"


def test_runtime_is_assembled_from_catalog_not_hardcoded_registration():
    runtime = build_runtime(ROOT)
    registrations = runtime.registry.list(status="active")
    assert len(registrations) == 1
    assert registrations[0].service_id == "repeat_case_service"


def test_unknown_service_returns_contract_error():
    response = build_runtime(ROOT).query(KnowledgeRequest(service_id="missing", query={"text": "x"}))
    assert response.success is False
    assert response.error is not None
    assert response.error.code == "SERVICE_NOT_FOUND"
    assert response.trace[-1].status == "failed"


def test_profile_validation_rejects_missing_adapter(tmp_path):
    profile_dir = tmp_path / "config" / "knowledge_services"
    profile_dir.mkdir(parents=True)
    (profile_dir / "bad.yaml").write_text(
        "service_id: bad\nservice_type: bad\nretrieval:\n  strategy: keyword\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError):
        ServiceProfileLoader(tmp_path).load("bad")
