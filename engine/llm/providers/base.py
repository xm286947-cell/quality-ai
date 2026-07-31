class BaseProvider:
    name = "base"

    def generate(self, prompt, context=None):
        raise NotImplementedError

    def health(self):
        return {"status": "ok"}
