# WP-03 Knowledge HTTP Client

## Scope

WP-03 connects the Business Agent runtime to Knowledge Capability through the frozen Knowledge Contract V1.0 HTTP endpoint.

```text
ExecutionRequest
  -> ExecutionRuntime
  -> KnowledgeHandler
  -> KnowledgeHttpClient
  -> POST /v1/knowledge/query
  -> Knowledge Capability Runtime
  -> ExecutionResponse
```

## Configuration

| Environment variable | Default |
|---|---|
| `KNOWLEDGE_HTTP_BASE_URL` | `http://127.0.0.1:8080` |
| `KNOWLEDGE_HTTP_QUERY_PATH` | `/v1/knowledge/query` |
| `KNOWLEDGE_HTTP_CONNECT_TIMEOUT` | `2.0` |
| `KNOWLEDGE_HTTP_READ_TIMEOUT` | `10.0` |
| `KNOWLEDGE_HTTP_MAX_RETRIES` | `1` |
| `KNOWLEDGE_HTTP_RETRY_BACKOFF` | `0.1` |

## Execution options

```json
{
  "knowledge": {
    "enabled": true,
    "service_id": "repeat_case_service",
    "top_k": 5,
    "filters": {},
    "requested_fields": [],
    "query_options": {}
  }
}
```

The query text is read from `options.knowledge.query_text`, then `input.text`, then `input.query`.

## Error mapping

Transport and Knowledge Contract errors are converted into Execution Contract errors while preserving `retryable`, HTTP status, failed step and Knowledge details.

## Verification

```bash
python run_wp03_check.py
```
