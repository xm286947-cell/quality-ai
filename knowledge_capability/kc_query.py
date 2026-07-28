from __future__ import annotations

import argparse
import json
from pathlib import Path

from knowledge_capability.contracts import KnowledgeRequest
from knowledge_capability.runtime import build_runtime

ROOT = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser(description="Knowledge Capability Contract Query")
    parser.add_argument("--service-id", default="repeat_case_service")
    parser.add_argument("--text", required=True)
    parser.add_argument("--top-k", type=int, default=None)
    parser.add_argument("--product", default="")
    parser.add_argument("--domain", default="")
    parser.add_argument("--cause-description", default="")
    parser.add_argument("--solution", default="")
    args = parser.parse_args()

    request = KnowledgeRequest(
        service_id=args.service_id,
        query={
            "text": args.text,
            "cause_description": args.cause_description,
            "solution": args.solution,
        },
        filters={"product": args.product, "domain": args.domain},
        options={"top_k": args.top_k} if args.top_k is not None else {},
        caller={"type": "cli"},
    )
    response = build_runtime(ROOT).query(request)
    print(json.dumps(response.to_dict(), ensure_ascii=False, indent=2))
    return 0 if response.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
