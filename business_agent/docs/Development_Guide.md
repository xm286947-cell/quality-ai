# Development Guide

## CLI

```bash
python main.py --help
python main.py list-agents
python main.py run-agent --help
```

## Test

```bash
python -m pytest -q
```

## Constraints

- 不修改冻结 Contract。
- 不在 Runtime 中加入具体 Agent 判断。
- Knowledge 访问必须经过 Contract Adapter。
- 联调问题优先通过配置、Adapter 或兼容层处理。
