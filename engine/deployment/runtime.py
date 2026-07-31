class RuntimeLifecycle:
    def __init__(self):
        self.status = "STOPPED"

    def start(self):
        self.status = "RUNNING"

    def stop(self):
        self.status = "STOPPED"

    def restart(self):
        self.stop()
        self.start()
