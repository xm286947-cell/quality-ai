from .state import EngineState

class LifecycleManager:
    def __init__(self):
        self.state = EngineState.CREATED

    def initialize(self):
        self.state = EngineState.INITIALIZED

    def start(self):
        self.state = EngineState.RUNNING

    def stop(self):
        self.state = EngineState.STOPPED

    def health(self):
        return {"state": self.state.value}
