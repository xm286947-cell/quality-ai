class AgentExecutor:
    def __init__(self, capability_registry=None):
        self.capability_registry = capability_registry

    def execute(self, agent, context):
        return agent.execute(context)
