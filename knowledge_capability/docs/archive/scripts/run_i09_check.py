from __future__ import annotations

import compileall
import subprocess
import sys
from pathlib import Path

from knowledge_capability.runtime.validation import validate_runtime_configuration

ROOT = Path(__file__).resolve().parent


def main() -> int:
    report = validate_runtime_configuration(ROOT)
    if not report.valid:
        print("[FAIL] Runtime configuration")
        for issue in report.issues:
            print(f"  - {issue}")
        return 1
    print(f"[PASS] Runtime configuration: {', '.join(report.services)}")

    command = [sys.executable, "-m", "pytest", "-q", "tests/integration", "tests/test_kc_runtime_i06.py", "tests/test_kc_runtime_i07.py", "tests/test_kc_runtime_i08.py"]
    completed = subprocess.run(command, cwd=ROOT, check=False)
    if completed.returncode != 0:
        print("[FAIL] I09 integration tests")
        return completed.returncode
    print("[PASS] I09 integration tests")

    if not compileall.compile_dir(ROOT / "knowledge_capability", quiet=1):
        print("[FAIL] Python compile check")
        return 1
    print("[PASS] Python compile check")
    print("I09 READY FOR BUSINESS AGENT INTEGRATION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
