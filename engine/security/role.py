class Role:
    def __init__(self, role_id, name=None, permissions=None):
        self.role_id = role_id
        self.name = name
        self.permissions = permissions or []

    def add_permission(self, permission):
        self.permissions.append(permission)
