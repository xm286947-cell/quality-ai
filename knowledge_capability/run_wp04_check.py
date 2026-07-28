from __future__ import annotations

import subprocess
import sys


def main() -> int:
    commands = [
        [sys.executable, "-m", "pytest", "-q", "tests/business_agent/test_wp04_execution_pipeline.py"],
        [sys.executable, "-m", "compileall", "-q", "business_agent"],
    ]
    for command in commands:
        completed = subprocess.run(command, check=False)
        if completed.returncode != 0:
            return completed.returncode
    print("[WP-04] EXECUTION PIPELINE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
