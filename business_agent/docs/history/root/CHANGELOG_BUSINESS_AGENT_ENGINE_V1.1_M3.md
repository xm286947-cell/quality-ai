# Changelog — BUSINESS_AGENT_ENGINE V1.1 M3

## Added

- Business-neutral Knowledge Contract client.
- Mock and HTTP Knowledge providers.
- Contract request/response data models.
- Tolerant response parser for flat and `data`-wrapped payloads.
- Knowledge workflow adapter and pre-analysis workflow node.
- Contract schemas and integration examples.
- Contract tests and command-line smoke test.

## Changed

- REPEAT_CASE plugin registers `knowledge.search` and `repeat_case.run_analysis`.
- REPEAT_CASE workflow version upgraded to 1.1.
- REPEAT_CASE output carries `platform_context.knowledge` when Knowledge is called.
- Agent version updated to `2.4-m6-platform-m3-contract-integration`.

## Compatibility

- Existing REPEAT_CASE business pipeline is unchanged.
- Mock is the default provider, so local execution does not require Knowledge Capability.
- Full regression: 132 tests passed.
