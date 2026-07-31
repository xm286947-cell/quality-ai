class TraceRecorder:
    def __init__(self):
        self.events = []

    def record(self, event):
        self.events.append(event)

    def list_events(self):
        return self.events
