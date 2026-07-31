from .state import WorkflowState

class Workflow:
    def __init__(self, definition):
        self.definition = definition
        self.state = WorkflowState.CREATED
        self.result = None
