class HealthCheck:
    def check(self, runtime=None):
        return {
            "service": "ok",
            "runtime": "ok" if runtime else "unknown"
        }
