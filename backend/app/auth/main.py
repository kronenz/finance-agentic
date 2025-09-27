"""
인증 및 권한 부여 메인 모듈
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from app.auth.jwt_handler import JWTHandler
from app.auth.rbac import rbac_manager, Role, Permission
from app.auth.dependencies import get_current_user, get_current_active_user
# from app.auth.two_factor import two_factor_auth  # 사용하지 않음
from app.auth.api_key import api_key_manager, APIKeyType
# from app.auth.session import session_manager  # 사용하지 않음
import logging

logger = logging.getLogger(__name__)

# FastAPI 라우터
router = APIRouter(prefix="/auth", tags=["authentication"])

# JWT 핸들러
jwt_handler = JWTHandler()

# 요청/응답 모델
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    two_factor_code: Optional[str] = None

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TwoFactorSetupResponse(BaseModel):
    qr_code: str
    backup_codes: List[str]
    secret: str

class TwoFactorVerifyRequest(BaseModel):
    code: str

class APIKeyCreateRequest(BaseModel):
    key_type: APIKeyType
    permissions: List[str]
    expires_days: Optional[int] = None

class APIKeyResponse(BaseModel):
    key_id: str
    secret: str
    key_type: APIKeyType
    permissions: List[str]
    expires_at: Optional[str] = None

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """사용자 로그인"""
    try:
        # TODO: 실제 사용자 인증 로직 구현
        user = await get_user_by_email(db, login_data.email)
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_data = {
            "sub": "user_123",
            "email": login_data.email,
            "role": Role.ADMIN,
            "permissions": ["trade:create", "trade:read", "ai_agent:control"],
            "is_active": True
        }
        
        # 2FA 검증 (구현된 경우)
        if login_data.two_factor_code:
            # TODO: 실제 2FA 검증 로직
            pass
        
        # JWT 토큰 생성
        access_token = jwt_handler.create_access_token(user_data)
        refresh_token = jwt_handler.create_refresh_token(user_data)
        
        # 세션 생성
        session_data = session_manager.create_session(
            user_id=user_data["sub"],
            user_data=user_data,
            ip_address="127.0.0.1",  # 실제로는 요청에서 추출
            user_agent="Mozilla/5.0"  # 실제로는 요청에서 추출
        )
        
        logger.info(f"User {login_data.email} logged in successfully")
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=jwt_handler.access_token_expire_minutes * 60,
            user=user_data
        )
        
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(refresh_data: RefreshTokenRequest):
    """토큰 갱신"""
    try:
        # 리프레시 토큰 검증
        payload = jwt_handler.verify_token(refresh_data.refresh_token, "refresh")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # 새로운 액세스 토큰 생성
        new_access_token = jwt_handler.refresh_access_token(refresh_data.refresh_token)
        if not new_access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to refresh token"
            )
        
        logger.info(f"Token refreshed for user: {payload.get('sub')}")
        
        return LoginResponse(
            access_token=new_access_token,
            refresh_token=refresh_data.refresh_token,
            expires_in=jwt_handler.access_token_expire_minutes * 60,
            user=payload
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """사용자 로그아웃"""
    try:
        # TODO: 세션 비활성화 로직
        logger.info(f"User {current_user.get('sub')} logged out")
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.post("/2fa/setup", response_model=TwoFactorSetupResponse)
async def setup_two_factor(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """2FA 설정"""
    try:
        user_email = current_user.get("email", "user@example.com")
        
        # 2FA 시크릿 생성
        secret = two_factor_auth.generate_secret(user_email)
        
        # QR 코드 생성
        qr_code = two_factor_auth.generate_qr_code(user_email, secret)
        
        # 백업 코드 생성
        backup_codes = two_factor_auth.generate_backup_codes()
        
        logger.info(f"2FA setup initiated for user: {user_email}")
        
        return TwoFactorSetupResponse(
            qr_code=qr_code,
            backup_codes=backup_codes,
            secret=secret
        )
        
    except Exception as e:
        logger.error(f"2FA setup failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="2FA setup failed"
        )

@router.post("/2fa/verify")
async def verify_two_factor(
    verify_data: TwoFactorVerifyRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """2FA 검증"""
    try:
        user = await get_user_by_email(db, request.email)
        if not user or not user.two_factor_secret:
            raise HTTPException(status_code=400, detail="2FA not enabled or user not found")
        user_secret = user.two_factor_secret
        
        # 2FA 코드 검증
        is_valid = two_factor_auth.verify_token(user_secret, verify_data.code)
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid 2FA code"
            )
        
        logger.info(f"2FA verified for user: {current_user.get('sub')}")
        
        return {"message": "2FA verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"2FA verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="2FA verification failed"
        )

@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    key_data: APIKeyCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """API 키 생성"""
    try:
        user_id = current_user.get("sub")
        
        # API 키 생성
        api_key_data = api_key_manager.generate_api_key(
            user_id=user_id,
            key_type=key_data.key_type,
            permissions=key_data.permissions,
            expires_days=key_data.expires_days
        )
        
        # TODO: 데이터베이스에 저장
        
        logger.info(f"API key created for user: {user_id}")
        
        return APIKeyResponse(
            key_id=api_key_data["key_id"],
            secret=api_key_data["secret"],
            key_type=api_key_data["key_type"],
            permissions=api_key_data["permissions"],
            expires_at=api_key_data["expires_at"].isoformat() if api_key_data["expires_at"] else None
        )
        
    except Exception as e:
        logger.error(f"API key creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key creation failed"
        )

@router.get("/me")
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """현재 사용자 정보 조회"""
    return {
        "user_id": current_user.get("sub"),
        "email": current_user.get("email"),
        "role": current_user.get("role"),
        "permissions": current_user.get("permissions", []),
        "is_active": current_user.get("is_active", True)
    }