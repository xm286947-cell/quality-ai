class Capability:
    def metadata(self):
        return {}

    def execute(self, context):
        raise NotImplementedError

    def health(self):
        return {"status": "ok"}
