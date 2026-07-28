from __future__ import annotations

import subprocess
import sys


def run(command: list[str]) -> None:
    print("[WP-02]", " ".join(command))
    subprocess.run(command, check=True)


if __name__ == "__main__":
    run([sys.executable, "-m", "pytest", "-q", "tests/execution"])
    run([sys.executable, "-m", "compileall", "-q", "business_agent"])
    print("[WP-02] BUSINESS AGENT RUNTIME PASS")
