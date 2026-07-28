from __future__ import annotations

import time
from collections.abc import Mapping
from typing import Any

import httpx

from .config import KnowledgeHttpConfig
from .errors import KnowledgeClientError


class KnowledgeHttpClient:
    """Business Agent -> Knowledge Capability HTTP client."""

    def __init__(
        self,
        config: KnowledgeHttpConfig | None = None,
        *,
        transport: httpx.BaseTransport | None = None,
        sleep=time.sleep,
    ) -> None:
        self.config = config or KnowledgeHttpConfig.from_env()
        self._sleep = sleep
        timeout = httpx.Timeout(
            connect=self.config.connect_timeout_seconds,
            read=self.config.read_timeout_seconds,
            write=self.config.read_timeout_seconds,
            pool=self.config.connect_timeout_seconds,
        )
        self._client = httpx.Client(timeout=timeout, transport=transport)

    def close(self) -> None:
        self._client.close()

    def query(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        body = dict(payload)
        last_error: KnowledgeClientError | None = None
        for attempt in range(self.config.max_retries + 1):
            try:
                response = self._client.post(self.config.query_url, json=body)
                return self._parse_response(response)
            except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout, httpx.WriteTimeout) as exc:
                last_error = KnowledgeClientError(
                    code="KNOWLEDGE_SERVICE_UNAVAILABLE",
                    message="Knowledge Capability HTTP service is unavailable",
                    retryable=True,
                    details={"error_type": type(exc).__name__, "attempt": attempt + 1},
                )
            except httpx.HTTPError as exc:
                last_error = KnowledgeClientError(
                    code="KNOWLEDGE_HTTP_ERROR",
                    message=str(exc) or "Knowledge HTTP request failed",
                    retryable=False,
                    details={"error_type": type(exc).__name__, "attempt": attempt + 1},
                )

            if last_error.retryable and attempt < self.config.max_retries:
                self._sleep(self.config.retry_backoff_seconds * (attempt + 1))
                continue
            raise last_error

        assert last_error is not None
        raise last_error

    @staticmethod
    def _parse_response(response: httpx.Response) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            raise KnowledgeClientError(
                code="KNOWLEDGE_RESPONSE_INVALID",
                message="Knowledge Capability returned non-JSON response",
                status_code=response.status_code,
                details={"body": response.text[:500]},
            ) from exc

        if not isinstance(payload, dict):
            raise KnowledgeClientError(
                code="KNOWLEDGE_RESPONSE_INVALID",
                message="Knowledge Capability response must be a JSON object",
                status_code=response.status_code,
            )

        if 200 <= response.status_code < 300 and payload.get("success") is True:
            return payload

        error = payload.get("error") if isinstance(payload.get("error"), dict) else {}
        code = str(error.get("code") or f"KNOWLEDGE_HTTP_{response.status_code}")
        message = str(error.get("message") or "Knowledge Capability request failed")
        retryable = bool(error.get("retryable")) or response.status_code in {429, 502, 503, 504}
        raise KnowledgeClientError(
            code=code,
            message=message,
            retryable=retryable,
            status_code=response.status_code,
            details={"knowledge_error": error, "response": payload},
        )
