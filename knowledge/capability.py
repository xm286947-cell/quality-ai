class KnowledgeCapability:
    def __init__(self, retriever=None):
        self.retriever = retriever

    def query(self, query_text):
        return self.retriever.retrieve(query_text) if self.retriever else []
