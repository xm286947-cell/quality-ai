# WP-02 Business Agent Runtime

## Purpose

WP-02 upgrades the WP-01 execution skeleton into a routable Business Agent runtime.

## Delivered capability

- AgentDefinition and AgentRegistry
- Agent ID based runtime routing
- enabled/disabled agent control
- operation validation
- execution lifecycle state
- partial trace preservation when a handler fails
- standard warning and artifact collection
- stable runtime error mapping

## Public entry

```python
from business_agent.runtime import ExecutionRuntime

response = ExecutionRuntime().execute({
    "contract_version": "V1.1",
    "agent_id": "repeat_case_agent",
    "input": {"text": "CAN receive congestion"}
})
```

## Next work package

WP-03 connects the `knowledge` handler to Knowledge Capability through HTTP.
