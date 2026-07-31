class TaskRequest:
    def __init__(self, workflow=None, input_data=None):
        self.workflow = workflow
        self.input_data = input_data


class TaskResponse:
    def __init__(self, task_id=None, status=None, result=None):
        self.task_id = task_id
        self.status = status
        self.result = result
