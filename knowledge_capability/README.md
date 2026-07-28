# KNOWLEDGE_CAPABILITY_ENGINE

## Current Status

| Item | Value |
|---|---|
| Version | V1.1 |
| Milestone | M1 |
| Work Package | WP-03 Knowledge HTTP Client |
| Status | WP-03 Delivered |
| Contracts | QUALITY_AGENT_CONTRACT V1.1 Execution Contract; V1.0 Knowledge Contract |
| Contract Status | Contract Freeze |
| Transports | Python In-Process, HTTP |
| Knowledge Service | `repeat_case_service` |

I12 adds an HTTP transport without changing the existing Knowledge Runtime, Repository, Provider or Repeat Case logic. HTTP requests and responses use the same frozen `QUALITY_AGENT_CONTRACT V1.0` as the in-process adapter.


## Business Agent Execution Layer

WP-01 adds the Client-to-Business-Agent execution boundary without changing the existing Knowledge Capability runtime.

```python
from business_agent.runtime import ExecutionRuntime

runtime = ExecutionRuntime()
response = runtime.execute({
    "contract_version": "V1.1",
    "request_id": "req-wp01-001",
    "agent_id": "repeat_case_agent",
    "input": {"text": "CAN接收拥堵导致软件保护重启"}
})
```

The public entry is `ExecutionRuntime.execute()`. Detailed guide: `docs/WP01_EXECUTION_LAYER.md`.


## Business Agent Knowledge HTTP Client

WP-03 replaces the Knowledge placeholder with a real HTTP client. Start Knowledge Capability first, then execute the Business Agent:

```bash
python -m knowledge_capability.api
```

```python
from business_agent.runtime import ExecutionRuntime

response = ExecutionRuntime().execute({
    "contract_version": "V1.1",
    "request_id": "req-wp03-001",
    "agent_id": "repeat_case_agent",
    "input": {"text": "CAN接收拥堵导致软件保护重启"},
    "options": {"knowledge": {"service_id": "repeat_case_service", "top_k": 5}}
})
```

Configuration and error mapping are documented in `docs/WP03_KNOWLEDGE_HTTP_CLIENT.md`.

## Install

Python 3.10 or later is recommended.

```bash
python -m pip install -r requirements.txt
```

## Start HTTP Service

```bash
python -m knowledge_capability.api
```

Equivalent command:

```bash
uvicorn knowledge_capability.api.app:app --host 0.0.0.0 --port 8080
```

Optional environment variables:

```text
KC_PROJECT_ROOT  Knowledge project root
KC_HOST          Default: 0.0.0.0
KC_PORT          Default: 8080
```

## Health Check

```bash
curl http://127.0.0.1:8080/health
```

Expected response:

```json
{
  "status": "UP",
  "capability": "knowledge_capability",
  "contract_version": "V1.0",
  "transport": "http"
}
```

## Knowledge Query API

Endpoint:

```text
POST /v1/knowledge/query
```

Example:

```bash
curl -X POST http://127.0.0.1:8080/v1/knowledge/query \
  -H "Content-Type: application/json" \
  -d '{
    "contract_version": "V1.0",
    "request_id": "req-http-001",
    "service_id": "repeat_case_service",
    "query": {
      "text": "CAN接收拥堵导致软件保护重启"
    },
    "filters": {},
    "requested_fields": [],
    "options": {
      "top_k": 5
    },
    "caller": {
      "type": "business_agent",
      "agent_id": "repeat_case_agent"
    }
  }'
```

The response contains:

```text
request_id
service_id
success
result
evidence
trace
warnings
error
contract_version
created_at
```

## Python In-Process Call

```python
from pathlib import Path

from knowledge_capability.adapters import BusinessAgentAdapter
from knowledge_capability.runtime import build_runtime

root = Path(__file__).resolve().parent
runtime = build_runtime(root)
adapter = BusinessAgentAdapter(runtime)
response = adapter.execute(payload)
```

## Existing CLI

Configuration validation:

```bash
python kc_validate.py
```

Repeat Case query:

```bash
python kc_query.py --text "软件运行过程中偶发崩溃" --top-k 5
```

## Test

WP-01 check:

```bash
python run_wp01_check.py
```

I12 HTTP check remains available:

```bash
python run_i12_check.py
```

Full regression:

```bash
python -m pytest -q
```

Current verified result:

```text
WP-01 Execution Layer checks: 6 passed
Full regression: 156 passed
```

## Main Structure

```text
business_agent/
├── contracts/execution/
├── handlers/
└── runtime/

knowledge_capability/
├── api/
│   ├── app.py
│   └── __main__.py
├── adapters/
├── contracts/
├── framework/
├── providers/
├── repository/
├── runtime/
└── services/

tests/
├── http/
└── integration/
```

More HTTP details: `docs/HTTP_SERVICE_GUIDE.md`.

## Current Boundary

I12 includes the Knowledge Capability HTTP server. Business Agent HTTP Provider integration is the next step. The existing in-process integration remains supported.


## WP-02 Business Agent Runtime

WP-02 upgrades the execution layer into a routable runtime:

- `AgentDefinition` and `AgentRegistry`
- agent routing and enable/disable control
- operation validation
- execution lifecycle status
- failed-step trace preservation
- warning and artifact collection

Run the WP-02 check:

```bash
python run_wp02_check.py
```

See `docs/WP02_BUSINESS_AGENT_RUNTIME.md`.


## WP-04 Execution Pipeline

The Business Agent now builds a knowledge-aware prompt, invokes an injectable model provider, and returns a standardized execution result. The default provider is deterministic and offline; production model providers can be injected through `LLMHandler`.

```bash
python run_wp04_check.py
```

See `docs/WP04_EXECUTION_PIPELINE.md`.

## Business Agent HTTP API

Start the Business Agent execution service:

```bash
python -m business_agent.api
```

Default endpoint:

```text
POST http://127.0.0.1:8090/v1/executions
```

The service accepts Execution Contract V1.1. It internally calls Knowledge Capability using Knowledge Contract V1.0. See `docs/WP05_FIRST_INTEGRATION.md` for the complete startup and integration procedure.
