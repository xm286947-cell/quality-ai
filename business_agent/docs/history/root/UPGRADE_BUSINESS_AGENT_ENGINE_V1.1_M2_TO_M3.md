# Upgrade Guide — M2 to M3

1. Replace the M2 project with this full package.
2. Keep `KNOWLEDGE_PROVIDER=mock` for local regression.
3. Run `pytest -q` and confirm all tests pass.
4. Configure the Knowledge Capability base URL and endpoint.
5. Run `scripts/knowledge_contract_smoke.py` against the live service.
6. Compare the live response fields with the frozen QUALITY_AGENT_CONTRACT V1.0 definitions.
7. Run REPEAT_CASE and inspect `output/agent_runs/<request_id>/trace.json`.

Rollback requires only setting:

```bash
KNOWLEDGE_PROVIDER=mock
```
