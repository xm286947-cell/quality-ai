class EngineServiceRuntime:
    def __init__(self, runtime=None, config=None):
        self.runtime = runtime
        self.config = config
        self.running = False

    def start(self):
        self.running = True
        if self.runtime:
            self.runtime.start()

    def stop(self):
        self.running = False
        if self.runtime:
            self.runtime.stop()

    def status(self):
        return "RUNNING" if self.running else "STOPPED"
