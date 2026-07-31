class Permission:
    def __init__(self, resource, action):
        self.resource = resource
        self.action = action

    def matches(self, resource, action):
        return self.resource == resource and self.action == action
