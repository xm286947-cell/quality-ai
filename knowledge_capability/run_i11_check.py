from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(label: str, command: list[str]) -> None:
    print(f"[I11] {label}")
    completed = subprocess.run(command, cwd=ROOT, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> None:
    run("validate configuration", [sys.executable, "kc_validate.py"])
    run(
        "contract and runtime regression",
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/integration",
            "tests/test_kc_runtime_i06.py",
            "tests/test_kc_runtime_i07.py",
            "tests/test_kc_runtime_i08.py",
        ],
    )
    run("compile project", [sys.executable, "-m", "compileall", "-q", "."])
    print("[I11] PROJECT CLEANUP CHECK PASS")


if __name__ == "__main__":
    main()
