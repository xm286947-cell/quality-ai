from __future__ import annotations

import json
from pathlib import Path

from knowledge_capability.runtime.validation import validate_runtime_configuration

ROOT = Path(__file__).resolve().parent


def main() -> int:
    report = validate_runtime_configuration(ROOT)
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    return 0 if report.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
