from .lifecycle import LifecycleManager

class AgentEngine:
    def __init__(self):
        self.lifecycle = LifecycleManager()

    def initialize(self):
        self.lifecycle.initialize()

    def start(self):
        self.lifecycle.start()

    def stop(self):
        self.lifecycle.stop()

    def health(self):
        return self.lifecycle.health()
