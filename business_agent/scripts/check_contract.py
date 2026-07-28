from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    pairs = [
        (ROOT / "contracts/quality_agent/knowledge_contract_v1.schema.json", "Knowledge Request"),
        (ROOT / "contracts/quality_agent/knowledge_response_v1.schema.json", "Knowledge Response"),
    ]
    for path, name in pairs:
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        print(f"[OK] {name}: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
