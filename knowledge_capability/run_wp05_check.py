from __future__ import annotations

import subprocess
import sys


def main() -> int:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "tests/integration/test_wp05_first_integration.py"],
        check=False,
    )
    if result.returncode == 0:
        print("[WP-05] FIRST INTEGRATION PASS")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
