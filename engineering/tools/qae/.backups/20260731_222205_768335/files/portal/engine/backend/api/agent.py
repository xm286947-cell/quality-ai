from fastapi import APIRouter
from registry.registry import list_agents, get_agent
from execution.manager import create_execution, update_status
from core.router import execute_mock_agent

router = APIRouter()

@router.get("/agents")
def agents():
    return [a.__dict__ for a in list_agents()]

@router.post("/agents/{agent_id}/execute")
def execute(agent_id: str, payload: dict):
    request_id = payload.get("request_id", "UNKNOWN")
    execution = create_execution(
        request_id,
        agent_id,
        payload
    )
    update_status(request_id, "RUNNING")
    result = execute_mock_agent(payload)
    update_status(request_id, "SUCCESS", result)
    return {
        "request_id": request_id,
        "status": "SUCCESS",
        "result": result
    }
