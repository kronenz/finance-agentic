"""
인증 관련 API 엔드포인트
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.auth import UserCreate, UserResponse, Token, LoginRequest
from app.services.auth_service import AuthService
from app.utils.security import create_access_token, verify_password
from app.models.user import User

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """사용자 회원가입"""
    auth_service = AuthService(db)
    
    # 이메일 중복 확인
    existing_user = await auth_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다."
        )
    
    # 사용자 생성
    user = await auth_service.create_user(user_data)
    return UserResponse.from_orm(user)

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """사용자 로그인"""
    auth_service = AuthService(db)
    
    # 사용자 인증
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # JWT 토큰 생성
    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 1800  # 30분
    }

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """사용자 로그아웃"""
    # 토큰을 블랙리스트에 추가하는 로직
    return {"message": "성공적으로 로그아웃되었습니다."}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """현재 사용자 정보 조회"""
    return UserResponse.from_orm(current_user)

@router.post("/forgot-password")
async def forgot_password(
    email: str,
    db: AsyncSession = Depends(get_db)
):
    """비밀번호 재설정 요청"""
    auth_service = AuthService(db)
    
    # 이메일로 비밀번호 재설정 링크 전송
    await auth_service.send_password_reset_email(email)
    
    return {"message": "비밀번호 재설정 링크가 이메일로 전송되었습니다."}

@router.post("/reset-password")
async def reset_password(
    token: str,
    new_password: str,
    db: AsyncSession = Depends(get_db)
):
    """비밀번호 재설정"""
    auth_service = AuthService(db)
    
    # 토큰 검증 및 비밀번호 재설정
    await auth_service.reset_password(token, new_password)
    
    return {"message": "비밀번호가 성공적으로 재설정되었습니다."}

@router.post("/verify-email")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """이메일 인증"""
    auth_service = AuthService(db)
    
    # 이메일 인증 토큰 검증
    await auth_service.verify_email_token(token)
    
    return {"message": "이메일이 성공적으로 인증되었습니다."}

# 의존성 함수들
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """현재 로그인한 사용자 조회"""
    auth_service = AuthService(db)
    
    # 토큰 검증
    user = await auth_service.get_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user
