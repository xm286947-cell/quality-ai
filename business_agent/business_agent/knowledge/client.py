from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .errors import KnowledgeConfigurationError, KnowledgeContractError, KnowledgeTransportError
from .models import KnowledgeRequest, KnowledgeResponse


class KnowledgeClient:
    """QUALITY_AGENT_CONTRACT V1.0 client with mock and HTTP providers."""

    def __init__(self, project_root: str | Path, config: dict[str, Any] | None = None) -> None:
        self.project_root = Path(project_root).resolve()
        self.config = dict(config or {})

    def search(self, request: KnowledgeRequest) -> KnowledgeResponse:
        provider = str(os.getenv("KNOWLEDGE_PROVIDER") or self.config.get("provider") or "mock").lower()
        started = time.perf_counter()
        if provider == "mock":
            response = self._mock_search(request)
        elif provider in {"capability", "http"}:
            response = self._http_search(request)
        else:
            raise KnowledgeConfigurationError(f"Unsupported knowledge provider: {provider}")
        if not response.request_id:
            response = KnowledgeResponse(**{**response.__dict__, "request_id": request.request_id})
        if response.contract_version not in {"1.0", "V1.0"}:
            raise KnowledgeContractError(
                f"Knowledge contract version mismatch: expected V1.0, got {response.contract_version}"
            )
        if response.elapsed_ms <= 0:
            response = KnowledgeResponse(
                **{**response.__dict__, "elapsed_ms": int((time.perf_counter() - started) * 1000)}
            )
        return response

    def _mock_search(self, request: KnowledgeRequest) -> KnowledgeResponse:
        fixture = self.config.get("fixture") or os.getenv("KNOWLEDGE_MOCK_FIXTURE")
        if fixture:
            path = Path(fixture)
            if not path.is_absolute():
                path = self.project_root / path
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload.setdefault("request_id", request.request_id)
            payload.setdefault("provider", "mock")
            return KnowledgeResponse.from_dict(payload)
        return KnowledgeResponse(
            request_id=request.request_id,
            status="SUCCESS",
            items=(),
            total=0,
            provider="mock",
            metadata={"query": request.query, "service_id": request.service_id},
        )

    def _http_search(self, request: KnowledgeRequest) -> KnowledgeResponse:
        base_url = str(os.getenv("KNOWLEDGE_BASE_URL") or self.config.get("base_url") or "").rstrip("/")
        endpoint = str(os.getenv("KNOWLEDGE_SEARCH_ENDPOINT") or self.config.get("endpoint") or "/v1/knowledge/query")
        if not base_url:
            raise KnowledgeConfigurationError("KNOWLEDGE_BASE_URL is required for capability provider")
        timeout = float(os.getenv("KNOWLEDGE_TIMEOUT_SECONDS") or self.config.get("timeout_seconds") or 30)
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        token = str(os.getenv("KNOWLEDGE_API_TOKEN") or self.config.get("token") or "")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        headers.update(dict(self.config.get("headers") or {}))
        http_request = Request(
            f"{base_url}{endpoint}",
            data=json.dumps(request.to_dict(), ensure_ascii=False).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urlopen(http_request, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise KnowledgeTransportError(f"Knowledge HTTP {exc.code}: {body[:500]}") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise KnowledgeTransportError(f"Knowledge request failed: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise KnowledgeContractError("Knowledge response is not valid JSON") from exc
        return KnowledgeResponse.from_dict(payload)
