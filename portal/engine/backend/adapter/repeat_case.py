from core.contract import AgentResponse

def execute(request):
    return AgentResponse(
        request_id=request["request_id"],
        agent_id="repeat_case",
        status="SUCCESS",
        result={
            "summary": "repeat case mock integration result",
            "source": "REPEAT_CASE_ENGINE"
        }
    )
