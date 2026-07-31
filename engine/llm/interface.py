class ModelInterface:
    def generate(self, prompt, context=None):
        raise NotImplementedError

    def health(self):
        return {"status": "unknown"}

    def metadata(self):
        return {}
