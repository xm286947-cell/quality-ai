# WP-01 Execution Layer

## Position

WP-01 implements the `QUALITY_AGENT_CONTRACT V1.1` Execution Contract boundary:

```text
Client
  | Execution Contract
  v
Business Agent
```

It does not implement the Knowledge HTTP Client. Knowledge integration remains a later work package.

## Public Entry

```python
from business_agent.runtime import ExecutionRuntime

runtime = ExecutionRuntime()
response = runtime.execute(
    {
        "contract_version": "V1.1",
        "request_id": "req-001",
        "agent_id": "repeat_case_agent",
        "input": {"text": "CAN接收拥堵导致软件保护重启"},
    }
)
```

## Contract Models

- `ExecutionRequest`
- `ExecutionResponse`
- `ExecutionContext`
- `ExecutionTrace`
- `ExecutionArtifact`
- `ExecutionError`

## Default Pipeline

```text
ContextHandler
  -> KnowledgeHandler
  -> PromptHandler
  -> LLMHandler
  -> ResultHandler
```

The Knowledge, Prompt and LLM handlers are stable extension points. WP-01 intentionally keeps them as non-network placeholders so later work packages can inject the real implementations without changing the Execution Contract.

## Verification

```bash
python run_wp01_check.py
python -m pytest -q
```
