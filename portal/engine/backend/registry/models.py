from dataclasses import dataclass

@dataclass
class AgentInfo:
    agent_id: str
    name: str
    version: str
    status: str = "active"
