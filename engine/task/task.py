from .state import TaskState

class Task:
    def __init__(self, task_id, workflow=None, input_data=None):
        self.task_id = task_id
        self.workflow = workflow
        self.input = input_data
        self.status = TaskState.CREATED
        self.result = None
