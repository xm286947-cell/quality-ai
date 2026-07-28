from __future__ import annotations

import argparse
import json
import mimetypes
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import uuid

ROOT = Path(__file__).resolve().parents[1]


def _multipart(fields: dict[str, str], file_path: Path) -> tuple[bytes, str]:
    boundary = f"----BusinessAgentBoundary{uuid.uuid4().hex}"
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.extend([
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
            str(value).encode("utf-8"), b"\r\n",
        ])
    content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    chunks.extend([
        f"--{boundary}\r\n".encode(),
        f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"\r\n'.encode(),
        f"Content-Type: {content_type}\r\n\r\n".encode(),
        file_path.read_bytes(), b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ])
    return b"".join(chunks), boundary


def _check_health(url: str, service_name: str) -> None:
    try:
        with urlopen(url, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise RuntimeError(f"{service_name} health check failed: {url}: {exc}") from exc
    status = str(payload.get("status") or "").upper()
    if status not in {"UP", "OK", "HEALTHY"}:
        raise RuntimeError(f"{service_name} is not healthy: {payload}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Real HTTP E2E: client -> Business Agent API -> Knowledge Capability API -> REPEAT_CASE")
    parser.add_argument("--base-url", default="http://127.0.0.1:8080", help="Business Agent API base URL")
    parser.add_argument("--knowledge-base-url", default="http://127.0.0.1:8000", help="Knowledge Capability base URL")
    parser.add_argument("--knowledge-endpoint", default="/v1/knowledge/query")
    parser.add_argument("--agent", default="repeat_case")
    parser.add_argument("--input", default="input/new_cases.xlsx")
    parser.add_argument("--request-id", default="")
    parser.add_argument("--query-id", default="")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--mock-ai", action="store_true", help="Only mock REPEAT_CASE AI analysis; Knowledge still uses HTTP")
    parser.add_argument("--skip-ai", action="store_true")
    parser.add_argument("--allow-mock-knowledge", action="store_true", help="Explicitly allow mock Knowledge; disabled by default")
    args = parser.parse_args()

    source = Path(args.input)
    if not source.is_absolute():
        source = ROOT / source
    if not source.exists():
        print(f"[ERROR] input file not found: {source}", file=sys.stderr)
        return 2

    provider = "mock" if args.allow_mock_knowledge else "http"
    try:
        _check_health(f"{args.base_url.rstrip('/')}/health", "Business Agent")
        if provider == "http":
            _check_health(f"{args.knowledge_base_url.rstrip('/')}/health", "Knowledge Capability")
    except RuntimeError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 3

    fields = {
        "request_id": args.request_id,
        "query_id": args.query_id,
        "top_k": str(args.top_k),
        "overwrite": "true",
        "mock": str(args.mock_ai).lower(),
        "skip_ai": str(args.skip_ai).lower(),
        "knowledge_provider": provider,
        "knowledge_base_url": args.knowledge_base_url,
        "knowledge_endpoint": args.knowledge_endpoint,
        "knowledge_timeout_seconds": "30",
    }
    body, boundary = _multipart(fields, source)
    url = f"{args.base_url.rstrip('/')}/v1/agents/{args.agent}/run"
    request = Request(url, data=body, method="POST", headers={
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Accept": "application/json",
    })
    print(f"POST {url}")
    print(f"Knowledge provider={provider}, base_url={args.knowledge_base_url}")
    try:
        with urlopen(request, timeout=300) as response:
            payload = json.loads(response.read().decode("utf-8"))
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0 if payload.get("status") == "SUCCESS" else 4
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"[HTTP {exc.code}] {detail}", file=sys.stderr)
        return 4
    except URLError as exc:
        print(f"[ERROR] Business Agent API unavailable: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
