from __future__ import annotations

from business_agent.contracts.execution import ExecutionContext
from business_agent.handlers import LLMHandler, PromptHandler, ResultHandler
from business_agent.llm import LLMProvider, ModelInvocation, ModelOutput
from business_agent.runtime import ExecutionPipeline, ExecutionRuntime


class FakeProvider(LLMProvider):
    def invoke(self, invocation: ModelInvocation) -> ModelOutput:
        assert "当前问题" in invocation.prompt
        return ModelOutput(text="发现一条高相关历史问题。", model="fake-v1", provider="test")


def make_context() -> ExecutionContext:
    return ExecutionContext(
        request_id="req-wp04",
        trace_id="trace-wp04",
        agent_id="repeat_case_agent",
        input={"text": "CAN接收拥堵导致重启"},
        knowledge={
            "status": "success",
            "result": {"results": [{"case_id": "CASE-001", "score": 0.92}]},
            "evidence": [{"evidence_id": "EV-001"}],
        },
    )


def test_prompt_uses_knowledge_result_and_evidence() -> None:
    context = PromptHandler().handle(make_context())
    assert context.prompt["status"] == "built"
    assert "CASE-001" in context.prompt["user"]
    assert "EV-001" in context.prompt["user"]


def test_llm_provider_is_injectable() -> None:
    context = PromptHandler().handle(make_context())
    context = LLMHandler(FakeProvider()).handle(context)
    assert context.model_result["status"] == "completed"
    assert context.model_result["provider"] == "test"


def test_result_contract_is_standardized() -> None:
    context = PromptHandler().handle(make_context())
    context = LLMHandler(FakeProvider()).handle(context)
    context = ResultHandler().handle(context)
    assert context.result["analysis"] == "发现一条高相关历史问题。"
    assert context.result["knowledge"]["candidate_count"] == 1
    assert context.result["knowledge"]["candidates"][0]["case_id"] == "CASE-001"


def test_runtime_pipeline_completes_without_external_llm() -> None:
    pipeline = ExecutionPipeline([PromptHandler(), LLMHandler(), ResultHandler()])
    runtime = ExecutionRuntime(pipeline)
    response = runtime.execute({
        "contract_version": "V1.1",
        "request_id": "req-runtime-wp04",
        "agent_id": "repeat_case_agent",
        "input": {"text": "无历史命中的问题"},
    })
    assert response.status == "success"
    assert response.result["model"]["provider"] == "builtin"
    assert "未检索到" in response.result["analysis"]
    assert [item.step for item in response.trace] == ["prompt", "llm", "result"]


def test_llm_requires_built_prompt() -> None:
    context = make_context()
    try:
        LLMHandler(FakeProvider()).handle(context)
    except ValueError as exc:
        assert "Prompt must be built" in str(exc)
    else:
        raise AssertionError("expected ValueError")
