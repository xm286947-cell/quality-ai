class RepeatCaseWorkflow:
    def __init__(self, agent):
        self.agent = agent

    def execute(self, request):
        return self.agent.analyze(request)
