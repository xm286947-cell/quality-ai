class KnowledgeRetriever:
    def __init__(self, repository=None):
        self.repository = repository

    def retrieve(self, query):
        if not self.repository:
            return []
        return self.repository.search(query)
