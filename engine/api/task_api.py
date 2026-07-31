class TaskAPI:
    def __init__(self, service):
        self.service = service

    def submit(self, task, context):
        return self.service.submit_task(task, context)

    def status(self, task):
        return self.service.get_task_status(task)
