class AccessControl:
    def check(self, user, resource, action):
        for role in user.roles:
            for permission in role.permissions:
                if permission.matches(resource, action):
                    return True
        return False
