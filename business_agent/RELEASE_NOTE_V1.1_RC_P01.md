# BUSINESS_AGENT_ENGINE V1.1 RC P01

## Scope

Execution API completion for REPEAT_CASE.

## Contract Boundary

- Client → Business Agent: multipart/form-data Execution Contract.
- Business Agent → Knowledge Capability: application/json Knowledge Contract.

## Main Changes

- Unified execution errors under `error.code`, `error.message`, `error.details`, and `error.request_id`.
- Added request validation and upload guards.
- Added `X-Request-ID` and `X-API-Version` response headers.
- Preserved `/docs` and `/openapi.json` as the formal API documentation entry.
- Removed the need to inspect or log raw multipart request bytes.

## Start

```bash
python -m business_agent.api
```

## API

- `GET /health`
- `GET /v1/agents`
- `POST /v1/agents/{agent_id}/run`
- `GET /docs`
- `GET /openapi.json`
