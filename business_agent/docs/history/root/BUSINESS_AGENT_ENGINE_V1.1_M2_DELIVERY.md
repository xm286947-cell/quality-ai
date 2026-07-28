# BUSINESS_AGENT_ENGINE V1.1 M2 Delivery

## Status
Development Complete / Ready for DryRun

## Baseline
BUSINESS_AGENT_ENGINE V1.1 M1 REPEAT_CASE Adapter

## M2 Goal
将 REPEAT_CASE 从 Runtime 内置 Adapter 注册方式迁移为标准 Agent Plugin，同时保持原有分析链路和命令兼容。

## Delivered
- Business-neutral `BusinessAgentRuntime`
- Dynamic `PluginLoader`
- Standard plugin asset directory
- External `agent.yaml` and `workflow.yaml`
- External input/output JSON schemas
- Prompt asset placeholder
- Common `ContextBuilder`
- Common `ResultEngine`
- Legacy `config/agents` fallback compatibility
- Existing REPEAT_CASE pipeline adapter retained behind plugin boundary

## Standard Plugin Layout
```
plugins/repeat_case/
├── agent.yaml
├── workflow.yaml
├── input.schema.json
├── output.schema.json
├── prompt.md
└── plugin.py
```

## Architecture Result
Runtime no longer imports `RepeatCaseAdapter` or contains REPEAT_CASE registration logic. The plugin owns handler registration.

## Verification
- Full regression: `129 passed`
- Existing CLI remains available
- Unified commands remain available:
  - `python main.py list-agents`
  - `python main.py run-agent --agent repeat_case ...`

## Known Boundary
M2 keeps the legacy end-to-end REPEAT_CASE analysis pipeline behind the plugin adapter. Internal pipeline stages will be migrated to common workflow nodes incrementally in later versions.
