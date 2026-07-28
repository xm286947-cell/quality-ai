from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(*args: str) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=ROOT, check=True)


if __name__ == "__main__":
    run(sys.executable, "kc_validate.py")
    run(sys.executable, "-m", "pytest", "-q", "tests/http", "tests/integration")
    run(sys.executable, "-m", "compileall", "-q", "knowledge_capability")
    print("I12 HTTP TRANSPORT CHECK PASS")
