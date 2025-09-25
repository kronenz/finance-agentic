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

PERMISSION_MAP = {
    Role.ADMIN: ["users:read", "users:write", "trades:read", "trades:write"],
    Role.TRADER: ["trades:read", "trades:write"],
    Role.VIEWER: ["trades:read"],
}

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