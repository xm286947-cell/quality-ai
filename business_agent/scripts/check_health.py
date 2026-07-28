from __future__ import annotations

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def main() -> int:
    base_url = os.getenv("KNOWLEDGE_BASE_URL", "http://127.0.0.1:8080").rstrip("/")
    try:
        with urlopen(f"{base_url}/health", timeout=5) as response:
            body = response.read().decode("utf-8")
            try:
                payload = json.loads(body)
            except json.JSONDecodeError:
                payload = body
            print(json.dumps({"http_status": response.status, "body": payload}, ensure_ascii=False, indent=2))
            return 0 if 200 <= response.status < 300 else 1
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        print(f"[ERROR] Knowledge health check failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
