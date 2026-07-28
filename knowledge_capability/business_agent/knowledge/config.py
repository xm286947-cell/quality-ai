from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeHttpConfig:
    base_url: str = "http://127.0.0.1:8080"
    query_path: str = "/v1/knowledge/query"
    connect_timeout_seconds: float = 2.0
    read_timeout_seconds: float = 10.0
    max_retries: int = 1
    retry_backoff_seconds: float = 0.1

    @classmethod
    def from_env(cls) -> "KnowledgeHttpConfig":
        return cls(
            base_url=os.getenv("KNOWLEDGE_HTTP_BASE_URL", cls.base_url).rstrip("/"),
            query_path=os.getenv("KNOWLEDGE_HTTP_QUERY_PATH", cls.query_path),
            connect_timeout_seconds=float(os.getenv("KNOWLEDGE_HTTP_CONNECT_TIMEOUT", str(cls.connect_timeout_seconds))),
            read_timeout_seconds=float(os.getenv("KNOWLEDGE_HTTP_READ_TIMEOUT", str(cls.read_timeout_seconds))),
            max_retries=max(0, int(os.getenv("KNOWLEDGE_HTTP_MAX_RETRIES", str(cls.max_retries)))),
            retry_backoff_seconds=max(0.0, float(os.getenv("KNOWLEDGE_HTTP_RETRY_BACKOFF", str(cls.retry_backoff_seconds)))),
        )

    @property
    def query_url(self) -> str:
        path = self.query_path if self.query_path.startswith("/") else f"/{self.query_path}"
        return f"{self.base_url}{path}"
