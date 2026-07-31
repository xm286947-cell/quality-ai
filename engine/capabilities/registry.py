class CapabilityRegistry:
    def __init__(self):
        self._capabilities = {}

    def register(self, capability):
        self._capabilities[capability.name] = capability

    def resolve(self, name):
        return self._capabilities.get(name)

    def list_capabilities(self):
        return list(self._capabilities.keys())
