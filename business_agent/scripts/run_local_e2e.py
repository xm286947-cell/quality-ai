from __future__ import annotations

"""Legacy local-process E2E runner. Use run_e2e.py for HTTP integration."""

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run REPEAT_CASE locally without Business Agent HTTP")
    parser.add_argument("--input", default="input/new_cases.xlsx")
    parser.add_argument("--query-id", default=None)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--mock-ai", action="store_true", default=True)
    args = parser.parse_args()

    cmd = [
        sys.executable, str(ROOT / "main.py"), "run-agent",
        "--agent", "repeat_case", "--input", args.input,
        "--top-k", str(args.top_k),
    ]
    if args.query_id:
        cmd.extend(["--query-id", args.query_id])
    if args.mock_ai:
        cmd.append("--mock")
    print(f"Knowledge provider: {os.getenv('KNOWLEDGE_PROVIDER', 'mock')}")
    return subprocess.call(cmd, cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
