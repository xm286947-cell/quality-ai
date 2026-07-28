from __future__ import annotations

import subprocess
import sys


COMMANDS = [
    [sys.executable, "-m", "pytest", "-q", "tests/execution"],
    [sys.executable, "-m", "compileall", "-q", "business_agent"],
]


def main() -> int:
    for command in COMMANDS:
        completed = subprocess.run(command, check=False)
        if completed.returncode != 0:
            return completed.returncode
    print("[WP-01] EXECUTION LAYER PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
