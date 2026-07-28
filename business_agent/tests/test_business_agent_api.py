from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from business_agent.api import app
from business_agent.models import RuntimeResult


client = TestClient(app, raise_server_exceptions=False)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "UP"
    assert response.json()["api_version"] == "v1"
    assert response.headers["X-API-Version"] == "v1"


def test_run_agent_upload_uses_http_entry(tmp_path: Path):
    source = tmp_path / "cases.json"
    source.write_text('[{"case_id":"Q1","query_text":"CAN拥堵导致重启"}]', encoding="utf-8")
    fake = RuntimeResult("RUN-HTTP-1", "repeat_case", "1.1", "SUCCESS", {"ok": True}, "trace.json")
    with patch("business_agent.api.BusinessAgentRuntime.run", return_value=fake) as run:
        with source.open("rb") as handle:
            response = client.post(
                "/v1/agents/repeat_case/run",
                files={"file": (source.name, handle, "application/json")},
                data={"request_id": "RUN-HTTP-1", "top_k": "5"},
            )
    assert response.status_code == 200
    assert response.json()["status"] == "SUCCESS"
    assert response.headers["X-Request-ID"] == "RUN-HTTP-1"
    request = run.call_args.args[0]
    assert request.agent_id == "repeat_case"
    assert Path(request.inputs["input"]).exists()


def test_invalid_top_k_uses_error_contract(tmp_path: Path):
    source = tmp_path / "cases.json"
    source.write_text("[]", encoding="utf-8")
    with source.open("rb") as handle:
        response = client.post(
            "/v1/agents/repeat_case/run",
            files={"file": (source.name, handle, "application/json")},
            data={"top_k": "0"},
        )
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "EXECUTION_REQUEST_VALIDATION_FAILED"
    assert body["error"]["request_id"]


def test_unsupported_upload_type_uses_error_contract(tmp_path: Path):
    source = tmp_path / "cases.exe"
    source.write_bytes(b"invalid")
    with source.open("rb") as handle:
        response = client.post(
            "/v1/agents/repeat_case/run",
            files={"file": (source.name, handle, "application/octet-stream")},
        )
    assert response.status_code == 415
    assert response.json()["error"]["code"] == "UNSUPPORTED_INPUT_TYPE"


def test_invalid_options_json_uses_error_contract(tmp_path: Path):
    source = tmp_path / "cases.json"
    source.write_text("[]", encoding="utf-8")
    with source.open("rb") as handle:
        response = client.post(
            "/v1/agents/repeat_case/run",
            files={"file": (source.name, handle, "application/json")},
            data={"options_json": "{"},
        )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_OPTIONS_JSON"
