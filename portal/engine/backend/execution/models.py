from dataclasses import dataclass, field

@dataclass
class Execution:
    request_id: str
    agent_id: str
    status: str = "CREATED"
    input: dict = field(default_factory=dict)
    output: dict = field(default_factory=dict)
