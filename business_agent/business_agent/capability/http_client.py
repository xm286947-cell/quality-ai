from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from .errors import CapabilityInvocationError


class JsonHttpCapabilityClient:
    """Standard-library JSON HTTP client for external capabilities."""

    def __init__(self, base_url: str, *, headers: dict[str, str] | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = {"Content-Type": "application/json", **(headers or {})}

    def invoke(
        self,
        operation: str,
        request: dict[str, Any],
        *,
        timeout_ms: int,
    ) -> dict[str, Any]:
        url = f"{self.base_url}/{operation}"
        body = json.dumps(request, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers=self.headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout_ms / 1000) as response:
                payload = response.read().decode("utf-8")
                return json.loads(payload)
        except urllib.error.HTTPError as exc:
            retryable = exc.code >= 500
            raise CapabilityInvocationError(
                f"HTTP {exc.code} invoking {operation}",
                retryable=retryable,
            ) from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise CapabilityInvocationError(
                f"transport error invoking {operation}: {exc}",
                retryable=True,
            ) from exc
        except json.JSONDecodeError as exc:
            raise CapabilityInvocationError(
                f"invalid JSON response invoking {operation}",
                retryable=False,
            ) from exc
