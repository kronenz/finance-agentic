"""
인증 및 권한 부여 의존성
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from app.auth.jwt_handler import JWTHandler
from app.auth.rbac import rbac_manager, Role, Permission
import logging

logger = logging.getLogger(__name__)

# HTTP Bearer 토큰 스키마
security = HTTPBearer()

# JWT 핸들러 인스턴스
jwt_handler = JWTHandler()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """현재 사용자 정보 조회"""
    token = credentials.credentials
    
    # 토큰 검증
    payload = jwt_handler.verify_token(token, "access")
    if not payload:
        logger.warning("Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload

async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """활성 사용자 정보 조회"""
    # 사용자 상태 확인 (예: 활성화된 사용자인지)
    if not current_user.get("is_active", True):
        logger.warning(f"Inactive user attempted access: {current_user.get('sub')}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user

async def get_current_admin_user(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
    """관리자 사용자 정보 조회"""
    if current_user.get("role") != Role.ADMIN:
        logger.warning(f"Non-admin user attempted admin access: {current_user.get('sub')}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user

async def get_current_trader_user(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
    """거래자 사용자 정보 조회"""
    if current_user.get("role") not in [Role.ADMIN, Role.TRADER]:
        logger.warning(f"Non-trader user attempted trader access: {current_user.get('sub')}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Trader access required"
        )
    
    return current_user

def require_permission_dependency(permission: Permission):
    """권한 확인 의존성 팩토리"""
    async def permission_checker(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
        rbac_manager.check_permission(current_user, permission)
        return current_user
    
    return permission_checker

def require_any_permission_dependency(permissions: list[Permission]):
    """여러 권한 중 하나라도 필요한 의존성 팩토리"""
    async def permission_checker(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
        if not rbac_manager.has_any_permission(current_user, permissions):
            logger.warning(f"Access denied: User {current_user.get('sub')} lacks any of permissions {permissions}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required one of: {permissions}"
            )
        return current_user
    
    return permission_checker

def require_all_permissions_dependency(permissions: list[Permission]):
    """모든 권한이 필요한 의존성 팩토리"""
    async def permission_checker(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
        if not rbac_manager.has_all_permissions(current_user, permissions):
            logger.warning(f"Access denied: User {current_user.get('sub')} lacks all permissions {permissions}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required all of: {permissions}"
            )
        return current_user
    
    return permission_checker

# 일반적인 권한 의존성들
require_trade_read = require_permission_dependency(Permission.TRADES_READ)
require_trade_write = require_permission_dependency(Permission.TRADES_WRITE)
require_user_read = require_permission_dependency(Permission.USERS_READ)
require_user_write = require_permission_dependency(Permission.USERS_WRITE)
require_monitoring_read = require_permission_dependency(Permission.MONITORING_READ)
require_monitoring_write = require_permission_dependency(Permission.MONITORING_WRITE)
require_ai_agent_read = require_permission_dependency(Permission.AI_AGENT_READ)
require_ai_agent_control = require_permission_dependency(Permission.AI_AGENT_CONTROL)
require_risk_read = require_permission_dependency(Permission.RISK_READ)
require_risk_update = require_permission_dependency(Permission.RISK_UPDATE)
require_system_admin = require_permission_dependency(Permission.SYSTEM_ADMIN)
