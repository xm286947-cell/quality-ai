class EngineServer:
    def __init__(self, bootstrap=None):
        self.bootstrap = bootstrap
        self.running = False

    def start(self):
        if self.bootstrap:
            self.bootstrap.start()
        self.running = True

    def stop(self):
        self.running = False

    def health(self):
        return {
            "service": "ok" if self.running else "stopped"
        }
