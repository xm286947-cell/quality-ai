from __future__ import annotations

import argparse
import json
from pathlib import Path

from business_agent.knowledge.client import KnowledgeClient
from business_agent.knowledge.models import KnowledgeRequest


def main() -> int:
    parser = argparse.ArgumentParser(description="QUALITY_AGENT_CONTRACT V1.0 smoke test")
    parser.add_argument("--provider", choices=("mock", "capability"), default="mock")
    parser.add_argument("--base-url", default="")
    parser.add_argument("--endpoint", default="/v1/knowledge/search")
    parser.add_argument("--query", default="重复问题联调测试")
    parser.add_argument("--service-id", default="repeat_case")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--fixture", default="tests/contract/mock_knowledge_response.json")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    config = {
        "provider": args.provider,
        "base_url": args.base_url,
        "endpoint": args.endpoint,
        "fixture": args.fixture if args.provider == "mock" else "",
    }
    response = KnowledgeClient(root, config).search(
        KnowledgeRequest("SMOKE-KNOWLEDGE-001", args.service_id, args.query, args.top_k)
    )
    print(json.dumps(response.to_dict(), ensure_ascii=False, indent=2))
    return 0 if response.status in {"SUCCESS", "PARTIAL"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
