class ResultAPI:
    def __init__(self, service):
        self.service = service

    def get(self, task):
        return self.service.get_result(task)
