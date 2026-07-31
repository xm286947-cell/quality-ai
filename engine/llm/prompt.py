class PromptTemplate:
    def __init__(self, template):
        self.template = template

    def render(self, variables=None):
        variables = variables or {}
        return self.template.format(**variables)
