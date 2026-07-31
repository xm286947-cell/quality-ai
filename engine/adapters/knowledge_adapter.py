class KnowledgeAdapter:
    def __init__(self, knowledge_service):
        self.name = "knowledge"
        self.knowledge_service = knowledge_service

    def metadata(self):
        return {"name": self.name}

    def execute(self, context):
        return self.knowledge_service.query(context.request)

    def health(self):
        return {"status": "ok"}
