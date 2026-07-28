from __future__ import annotations

import httpx
import pytest

from business_agent.knowledge import KnowledgeClientError, KnowledgeHttpClient, KnowledgeHttpConfig


def config(**overrides):
    values = dict(
        base_url="http://knowledge.test",
        query_path="/v1/knowledge/query",
        connect_timeout_seconds=0.1,
        read_timeout_seconds=0.1,
        max_retries=0,
        retry_backoff_seconds=0.0,
    )
    values.update(overrides)
    return KnowledgeHttpConfig(**values)


def test_query_success():
    def handler(request: httpx.Request):
        assert request.url.path == "/v1/knowledge/query"
        return httpx.Response(200, json={
            "request_id": "req-1", "service_id": "repeat_case_service", "success": True,
            "result": {"results": [{"case_id": "CASE-001"}]}, "evidence": [], "trace": [],
            "warnings": [], "error": None, "contract_version": "V1.0", "created_at": "now",
        })

    client = KnowledgeHttpClient(config(), transport=httpx.MockTransport(handler))
    response = client.query({"request_id": "req-1"})
    assert response["success"] is True
    assert response["result"]["results"][0]["case_id"] == "CASE-001"


def test_service_error_mapping():
    client = KnowledgeHttpClient(
        config(),
        transport=httpx.MockTransport(lambda request: httpx.Response(404, json={
            "success": False,
            "error": {"code": "SERVICE_NOT_FOUND", "message": "missing", "retryable": False},
        })),
    )
    with pytest.raises(KnowledgeClientError) as exc:
        client.query({})
    assert exc.value.code == "SERVICE_NOT_FOUND"
    assert exc.value.status_code == 404


def test_retry_service_unavailable_then_success():
    calls = {"count": 0}

    def handler(request: httpx.Request):
        calls["count"] += 1
        if calls["count"] == 1:
            raise httpx.ConnectError("offline", request=request)
        return httpx.Response(200, json={"success": True, "result": {}, "evidence": [], "trace": []})

    client = KnowledgeHttpClient(
        config(max_retries=1), transport=httpx.MockTransport(handler), sleep=lambda _: None
    )
    assert client.query({})["success"] is True
    assert calls["count"] == 2


def test_invalid_json_response():
    client = KnowledgeHttpClient(
        config(), transport=httpx.MockTransport(lambda request: httpx.Response(200, text="not-json"))
    )
    with pytest.raises(KnowledgeClientError) as exc:
        client.query({})
    assert exc.value.code == "KNOWLEDGE_RESPONSE_INVALID"
