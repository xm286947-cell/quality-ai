# Architecture

```text
REPEAT_CASE Plugin
        ↓
BUSINESS_AGENT_ENGINE Runtime
        ↓
Workflow / Context / Result / Trace
        ↓
KnowledgeContractAdapter
        ↓
QUALITY_AGENT_CONTRACT V1.0
        ↓
Knowledge Capability
```

Runtime 不包含具体业务智能体分支。业务行为由 `plugins/<agent_id>/` 中的配置与 Plugin 提供。
