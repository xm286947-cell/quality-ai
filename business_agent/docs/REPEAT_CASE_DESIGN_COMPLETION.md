# REPEAT_CASE Design Completion

Version: BUSINESS_AGENT_ENGINE V1.1 RC
Status: Code Complete / Test Passed

## Completed scope

1. Client invokes Business Agent only through HTTP.
2. Business Agent receives Excel/JSON and parses it on the service side.
3. Parsed cases are normalized before Knowledge access.
4. Every case calls Knowledge Capability through QUALITY_AGENT_CONTRACT V1.0 HTTP request.
5. Empty query fails locally and is never sent to Knowledge.
6. Knowledge HTTP configuration is explicitly supplied to the Business Agent API.
7. REPEAT_CASE continues analysis and returns Runtime output and trace path.
8. E2E performs health checks and never silently falls back to mock Knowledge.

## Acceptance commands

```bash
python -m business_agent.api
```

```bash
python scripts/run_e2e.py \
  --base-url http://127.0.0.1:8080 \
  --knowledge-base-url http://127.0.0.1:8000 \
  --input input/new_cases.xlsx \
  --top-k 5
```

## Automated verification

```text
138 passed
```
