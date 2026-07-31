from fastapi import APIRouter
from registry.registry import list_agents
from core.router import route

router = APIRouter()

@router.get("/agents")
def agents():
    return [a.__dict__ for a in list_agents()]


@router.post("/agents/{agent_id}/execute")
def execute(agent_id: str, payload: dict):
    request = {
        "request_id": payload.get("request_id", "UNKNOWN"),
        "agent_id": agent_id,
        "payload": payload
    }

    response = route(agent_id, request)

    return {
        "request_id": response.request_id,
        "agent_id": response.agent_id,
        "status": response.status,
        "result": response.result
    }
