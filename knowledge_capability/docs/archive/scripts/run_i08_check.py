from __future__ import annotations

import compileall
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(command: list[str]) -> None:
    print("\n$ " + " ".join(command))
    completed = subprocess.run(command, cwd=ROOT)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> int:
    run([sys.executable, "kc_validate.py"])
    run([
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "tests/test_kc_runtime_i06.py",
        "tests/test_kc_runtime_i07.py",
        "tests/test_kc_runtime_i08.py",
    ])
    print("\n$ python compileall")
    if not compileall.compile_dir(ROOT / "knowledge_capability", quiet=1):
        return 1
    print("\nI08 check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
