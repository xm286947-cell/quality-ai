# Knowledge Capability HTTP Service Guide

## Start

```bash
python -m pip install -r requirements.txt
python -m knowledge_capability.api
```

Equivalent command:

```bash
uvicorn knowledge_capability.api.app:app --host 0.0.0.0 --port 8080
```

Environment variables:

```text
KC_PROJECT_ROOT  Project root; defaults to current packaged project
KC_HOST          Default 0.0.0.0
KC_PORT          Default 8080
```

## Health

```bash
curl http://127.0.0.1:8080/health
```

## Query

```bash
curl -X POST http://127.0.0.1:8080/v1/knowledge/query \
  -H "Content-Type: application/json" \
  -d '{
    "contract_version": "V1.0",
    "request_id": "req-http-001",
    "service_id": "repeat_case_service",
    "query": {"text": "CAN接收拥堵导致软件保护重启"},
    "filters": {},
    "requested_fields": [],
    "options": {"top_k": 5},
    "caller": {"type": "business_agent", "agent_id": "repeat_case_agent"}
  }'
```

The request and response use `QUALITY_AGENT_CONTRACT V1.0`. HTTP is only the transport layer.
