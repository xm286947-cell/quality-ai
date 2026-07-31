class ExecutionContext:
    def __init__(self, task_id, request=None):
        self.task_id = task_id
        self.request = request
        self.metadata = {}
        self.result = None
