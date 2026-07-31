class LLMRuntime:
    def __init__(self, provider=None):
        self.provider = provider

    def generate(self, prompt, context=None):
        if not self.provider:
            raise RuntimeError("LLM provider not configured")
        return self.provider.generate(prompt, context)
