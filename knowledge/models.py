class KnowledgeItem:
    def __init__(self, item_id=None, title=None, content=None, metadata=None):
        self.item_id = item_id
        self.title = title
        self.content = content
        self.metadata = metadata or {}


class KnowledgeQuery:
    def __init__(self, query_text=None, context=None):
        self.query_text = query_text
        self.context = context or {}
