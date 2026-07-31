class EngineBootstrap:
    def __init__(self, config=None):
        self.config = config
        self.components = {}

    def register(self, name, component):
        self.components[name] = component

    def initialize(self):
        return True

    def start(self):
        self.initialize()
        return True
