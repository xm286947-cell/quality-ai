class StepDefinition:
    def __init__(self, name, agent=None):
        self.name = name
        self.agent = agent


class WorkflowDefinition:
    def __init__(self, name, steps=None):
        self.name = name
        self.steps = steps or []

    def add_step(self, step):
        self.steps.append(step)
