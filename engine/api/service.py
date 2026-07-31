class EngineService:
    def __init__(self, task_executor=None):
        self.task_executor = task_executor

    def submit_task(self, task, context):
        return self.task_executor.execute(task, context)

    def get_task_status(self, task):
        return task.status.value

    def get_result(self, task):
        return task.result
