from dataclasses import dataclass, field

@dataclass
class AgentRequest:
    request_id: str
    agent_id: str
    payload: dict = field(default_factory=dict)
    context: dict = field(default_factory=dict)


@dataclass
class AgentResponse:
    request_id: str
    agent_id: str
    status: str
    result: dict = field(default_factory=dict)
    report: str = ""
