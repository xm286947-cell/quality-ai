from __future__ import annotations

import subprocess
import sys


COMMANDS = [
    [sys.executable, "-m", "pytest", "-q", "tests/business_agent/test_wp03_knowledge_http_client.py", "tests/business_agent/test_wp03_runtime_http_integration.py"],
    [sys.executable, "-m", "pytest", "-q"],
]


def main() -> int:
    for command in COMMANDS:
        result = subprocess.run(command, check=False)
        if result.returncode != 0:
            print("[WP-03] KNOWLEDGE HTTP CLIENT FAIL")
            return result.returncode
    print("[WP-03] KNOWLEDGE HTTP CLIENT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
