# BUSINESS_AGENT_ENGINE V1.1 M3

## Delivery Scope

REPEAT_CASE × Knowledge Capability integration preparation.

## Implemented

- `KnowledgeClient`: mock and HTTP/capability providers.
- `KnowledgeContractAdapter`: maps Runtime Context to Knowledge Contract request/response.
- Standard contract DTOs and JSON schemas under `contracts/quality_agent/`.
- Configuration-only provider switching through runtime options or environment variables.
- Knowledge workflow node before the existing REPEAT_CASE analysis node.
- Knowledge result injected into platform context without changing repeat-case analysis logic.
- Trace summary includes provider, latency, recall count and evidence count.
- Mock fixture, contract unit tests and smoke-test script.
- Existing regression suite remains green.

## Runtime Configuration

Environment variables:

```bash
KNOWLEDGE_PROVIDER=capability
KNOWLEDGE_BASE_URL=http://127.0.0.1:8080
KNOWLEDGE_SEARCH_ENDPOINT=/v1/knowledge/search
KNOWLEDGE_TIMEOUT_SECONDS=30
```

Optional bearer token:

```bash
KNOWLEDGE_API_TOKEN=...
```

## Smoke Test

Mock:

```bash
python scripts/knowledge_contract_smoke.py --provider mock
```

Real capability:

```bash
python scripts/knowledge_contract_smoke.py \
  --provider capability \
  --base-url http://127.0.0.1:8080 \
  --endpoint /v1/knowledge/search \
  --query "CAN接收处理拥堵导致重启"
```

## Regression

```text
132 passed
```

## Integration Boundary

This milestone validates Contract transport, configuration switching, response parsing, context delivery and traceability. The original local REPEAT_CASE retrieval and decision pipeline is retained; replacing its internal retrieval with Knowledge Capability output is the next joint-integration step after the live endpoint and frozen field mapping are verified.
