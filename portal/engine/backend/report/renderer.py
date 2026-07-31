def render(response):
    return {
        "agent_id": response.agent_id,
        "request_id": response.request_id,
        "status": response.status,
        "result": response.result
    }
