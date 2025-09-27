"""
Role-based access control.
"""
from functools import wraps
from fastapi import HTTPException, Depends

from app.models.user import User
from app.auth.jwt import get_current_user

class Role:
    ADMIN = "admin"
    TRADER = "trader"
    VIEWER = "viewer"

class Permission:
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    TRADES_READ = "trades:read"
    TRADES_WRITE = "trades:write"
    MONITORING_READ = "monitoring:read"
    MONITORING_WRITE = "monitoring:write"
    AI_AGENT_READ = "ai_agent:read"
    AI_AGENT_CONTROL = "ai_agent:control"
    RISK_READ = "risk:read"
    RISK_UPDATE = "risk:update"
    SYSTEM_ADMIN = "system:admin"

PERMISSION_MAP = {
    Role.ADMIN: [Permission.USERS_READ, Permission.USERS_WRITE, Permission.TRADES_READ, Permission.TRADES_WRITE, Permission.MONITORING_READ, Permission.MONITORING_WRITE, Permission.AI_AGENT_READ, Permission.AI_AGENT_CONTROL, Permission.RISK_READ, Permission.RISK_UPDATE, Permission.SYSTEM_ADMIN],
    Role.TRADER: [Permission.TRADES_READ, Permission.TRADES_WRITE, Permission.MONITORING_READ, Permission.AI_AGENT_READ, Permission.RISK_READ],
    Role.VIEWER: [Permission.TRADES_READ, Permission.MONITORING_READ, Permission.AI_AGENT_READ],
}

class RBACManager:
    """Role-based access control manager"""
    
    def __init__(self):
        self.permission_map = PERMISSION_MAP
    
    def get_user_permissions(self, user: User) -> list[str]:
        """사용자의 권한 목록 반환"""
        return self.permission_map.get(user.role, [])
    
    def has_permission(self, user: User, permission: str) -> bool:
        """사용자가 특정 권한을 가지고 있는지 확인"""
        user_permissions = self.get_user_permissions(user)
        return permission in user_permissions
    
    def has_any_permission(self, user: User, permissions: list[str]) -> bool:
        """사용자가 권한 목록 중 하나라도 가지고 있는지 확인"""
        user_permissions = self.get_user_permissions(user)
        return any(p in user_permissions for p in permissions)

# 전역 RBAC 매니저 인스턴스
rbac_manager = RBACManager()

def rbac_required(required_permissions: list[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user: User = kwargs.get("current_user")
            if not user:
                # Try to get user from dependencies if not in kwargs
                for arg in args:
                    if isinstance(arg, User):
                        user = arg
                        break
            
            if not user:
                raise HTTPException(status_code=403, detail="Forbidden: User not found")

            user_permissions = []
            for role in user.roles:
                user_permissions.extend(PERMISSION_MAP.get(role, []))
            
            if not any(p in user_permissions for p in required_permissions):
                raise HTTPException(status_code=403, detail=f"Forbidden: Missing required permissions: {required_permissions}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator