from .models import AgentInfo

_agents = {}

def register_agent(agent: AgentInfo):
    _agents[agent.agent_id] = agent

def get_agent(agent_id: str):
    return _agents.get(agent_id)

def list_agents():
    return list(_agents.values())

register_agent(
    AgentInfo(
        agent_id="mock_agent",
        name="Mock Agent",
        version="V1.0"
    )
)
