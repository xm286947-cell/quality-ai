from .state import TaskState

class TaskExecutor:
    def __init__(self, workflow_executor=None):
        self.workflow_executor = workflow_executor

    def execute(self, task, context):
        task.status = TaskState.RUNNING

        try:
            result = self.workflow_executor.execute(
                task.workflow,
                context
            )
            task.result = result
            task.status = TaskState.COMPLETED
            return result

        except Exception:
            task.status = TaskState.FAILED
            raise
