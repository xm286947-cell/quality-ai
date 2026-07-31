class User:
    def __init__(self, user_id, name=None, roles=None):
        self.user_id = user_id
        self.name = name
        self.roles = roles or []
