class KnowledgeRepository:
    def __init__(self, items=None):
        self.items = items or []

    def search(self, query):
        return [
            item for item in self.items
            if query.lower() in (item.content or "").lower()
        ]
