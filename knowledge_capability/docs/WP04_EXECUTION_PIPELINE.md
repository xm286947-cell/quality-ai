# WP-04 Execution Pipeline

## Scope

WP-04 completes the executable Business Agent pipeline after Knowledge retrieval.

```text
ExecutionRequest
  -> ContextHandler
  -> KnowledgeHandler
  -> PromptHandler
  -> LLMHandler
  -> ResultHandler
  -> ExecutionResponse
```

## Prompt

`PromptHandler` consumes the query, knowledge candidates and evidence. It creates a stable prompt object containing `system`, `user`, `template_id` and normalized variables.

## Model provider

`LLMHandler` depends on the `LLMProvider` interface. The default provider is deterministic and offline so the full runtime remains executable without external credentials. A production model provider can be injected without changing the pipeline or Execution Contract.

## Result

The result includes analysis text, normalized candidate knowledge, evidence and model metadata. Compatibility fields `accepted` and `knowledge.result` remain available.

## Check

```bash
python run_wp04_check.py
python -m pytest -q
```
