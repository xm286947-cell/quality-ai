# Plugin Development

标准插件目录：

```text
plugins/<agent_id>/
├── agent.yaml
├── workflow.yaml
├── input.schema.json
├── output.schema.json
├── prompt.md
└── plugin.py
```

`plugin.py` 只负责向 Handler Registry 注册业务 Handler。Runtime 不得通过 `if agent == ...` 识别业务智能体。
