from adapter.repeat_case import execute as repeat_case_execute

def route(agent_id, request):
    if agent_id == "repeat_case":
        return repeat_case_execute(request)

    raise ValueError(f"Unsupported agent: {agent_id}")
