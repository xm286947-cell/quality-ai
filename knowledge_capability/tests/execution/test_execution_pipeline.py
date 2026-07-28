from business_agent.contracts.execution import ExecutionContext
from business_agent.handlers import ExecutionHandler
from business_agent.runtime import ExecutionPipeline


class MarkerHandler(ExecutionHandler):
    name = "marker"

    def handle(self, context: ExecutionContext) -> ExecutionContext:
        context.variables["marked"] = True
        return context


def test_pipeline_runs_handler_and_creates_trace():
    pipeline = ExecutionPipeline([MarkerHandler()])
    context = ExecutionContext(request_id="req-1", trace_id="trace-1", agent_id="agent-1")
    result, trace = pipeline.run(context)
    assert result.variables["marked"] is True
    assert trace[0].step == "marker"
    assert trace[0].status == "success"
    assert trace[0].duration_ms is not None
