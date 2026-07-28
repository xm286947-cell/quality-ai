from pathlib import Path

from knowledge_capability.contracts import KnowledgeRequest
from knowledge_capability.repository import RepositorySearchResult
from knowledge_capability.services import RepeatCaseKnowledgeService
from knowledge_capability.sources import KnowledgeSourceRegistry
from knowledge_capability.runtime import build_runtime

ROOT = Path(__file__).resolve().parents[1]


class FakeRepository:
    def search(self, query, *, filters=None, options=None):
        return RepositorySearchResult(
            payload={"results": [{"case_id": "CASE-1", "score": 0.91}]},
            provider_type="fake",
            source_id="fake-source",
            result_count=1,
        )

    def get(self, knowledge_id):
        return None

    def list(self, filters=None):
        return []

    def metadata(self):
        return {"provider_type": "fake"}


def test_knowledge_source_registry_resolves_repeat_case_source():
    source = KnowledgeSourceRegistry(ROOT).get("repeat_case_json")
    assert source.service_id == "repeat_case_service"
    assert source.provider_type == "json_repository"
    assert source.schema_type == "repeat_case"


def test_repeat_case_service_depends_on_repository_contract():
    service = RepeatCaseKnowledgeService(FakeRepository())
    response = service.handle(KnowledgeRequest(service_id="repeat_case_service", query={"text": "x"}))
    assert response.success is True
    assert response.result["results"][0]["case_id"] == "CASE-1"
    assert response.trace[0].stage == "repository_resolution"
    assert response.trace[0].details["source_id"] == "fake-source"
    assert response.evidence[0].metadata["source_id"] == "fake-source"


def test_runtime_assembles_repository_and_provider_boundary():
    runtime = build_runtime(ROOT)
    handler = runtime.registry.get("repeat_case_service").handler
    metadata = handler.repository.metadata()
    assert metadata["source_id"] == "repeat_case_json"
    assert metadata["provider_type"] == "json_repository"
