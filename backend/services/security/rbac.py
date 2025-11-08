class RoleBasedAccessControl:
    def __init__(self):
        self.permissions = {
            "admin": ["read", "write", "delete", "migrate", "configure", "manage_users"],
            "operator": ["read", "write", "migrate"],
            "viewer": ["read"]
        }
    def authorize_action(self, user_role: str, action: str) -> bool:
        user_permissions = self.permissions.get(user_role, [])
        return action in user_permissions
    def get_user_permissions(self, user_role: str) -> list:
        return self.permissions.get(user_role, [])
    def can_access_resource(self, user_role: str, resource_type: str, action: str) -> bool:
        if user_role == "admin":
            return True
        if resource_type == "data_object":
            return action in self.permissions.get(user_role, [])
        if resource_type == "migration_job":
            return action in ["read", "migrate"] and self.authorize_action(user_role, action)
        if resource_type == "policy":
            return user_role == "admin"
        return False
    def validate_role(self, role: str) -> bool:
        return role in self.permissions
