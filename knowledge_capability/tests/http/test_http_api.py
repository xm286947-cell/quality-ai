from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from knowledge_capability.api.app import create_app

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_health():
    client = TestClient(create_app(PROJECT_ROOT))
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "UP"
    assert response.json()["contract_version"] == "V1.0"


def test_query_rejects_invalid_contract():
    client = TestClient(create_app(PROJECT_ROOT))
    response = client.post(
        "/v1/knowledge/query",
        json={"contract_version": "V9.0", "service_id": "repeat_case_service", "query": {}},
    )
    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_REQUEST"


def test_query_unknown_service():
    client = TestClient(create_app(PROJECT_ROOT))
    response = client.post(
        "/v1/knowledge/query",
        json={
            "contract_version": "V1.0",
            "request_id": "http-unknown-service",
            "service_id": "missing_service",
            "query": {"text": "demo"},
            "caller": {"type": "business_agent", "agent_id": "test"},
        },
    )
    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "SERVICE_NOT_FOUND"
    assert body["request_id"] == "http-unknown-service"
