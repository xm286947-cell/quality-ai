# WP-05 First Integration

## Scope

WP-05 completes the first executable integration chain:

```text
Client
  -> POST /v1/executions
Business Agent API
  -> ExecutionRuntime
  -> KnowledgeHttpClient
  -> POST /v1/knowledge/query
Knowledge Capability API
  -> repeat_case_service
  -> Knowledge response
Business Agent Pipeline
  -> Prompt
  -> LLM Provider
  -> Result
  -> ExecutionResponse
```

## Contract boundary

The client sends only Execution Contract V1.1. `service_id`, retrieval options and other Knowledge Contract fields must be placed under `options.knowledge`; top-level Knowledge Contract fields are rejected by Execution Contract validation.

## Start services

Knowledge Capability:

```bash
python prepare_i10_fixture.py
python -m knowledge_capability.api
```

Business Agent:

```bash
export KNOWLEDGE_HTTP_BASE_URL=http://127.0.0.1:8080
python -m business_agent.api
```

Business Agent defaults to port `8090` and Knowledge Capability defaults to port `8080`.

## Execute

```bash
curl -X POST http://127.0.0.1:8090/v1/executions \
  -H 'Content-Type: application/json' \
  -d '{
    "contract_version":"V1.1",
    "request_id":"wp05-demo-001",
    "agent_id":"repeat_case_agent",
    "input":{"text":"CAN接收拥堵导致软件保护重启"},
    "options":{"knowledge":{"service_id":"repeat_case_service","top_k":3}}
  }'
```

## Acceptance

- Business Agent health endpoint is available.
- Execution Contract is validated at the Business Agent boundary.
- Knowledge Contract is generated only inside Business Agent.
- Knowledge query reaches `repeat_case_service` over HTTP transport.
- Prompt, model provider and result stages execute after retrieval.
- Trace contains context, knowledge, prompt, llm and result stages.
