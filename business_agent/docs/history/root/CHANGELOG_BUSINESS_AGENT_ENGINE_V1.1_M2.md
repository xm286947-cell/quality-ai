# Changelog — BUSINESS_AGENT_ENGINE V1.1 M2

## Added
- `business_agent/plugin/loader.py`
- `business_agent/context/builder.py`
- `business_agent/result/engine.py`
- Standard `plugins/repeat_case` package and assets

## Changed
- Runtime now loads plugin behavior dynamically.
- Agent profile loader prioritizes standard plugin profiles and supports legacy fallback.
- Agent profile model records plugin configuration and asset directory.

## Compatibility
- No legacy REPEAT_CASE command removed.
- Existing analysis pipeline remains unchanged.
- Existing test suite remains green.

## Test Result
`129 passed`
