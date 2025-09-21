"""
인증 관련 Pydantic 스키마
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    """사용자 기본 스키마"""
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    country: Optional[str] = None
    timezone: str = "UTC"

class UserCreate(UserBase):
    """사용자 생성 스키마"""
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('비밀번호는 최소 8자 이상이어야 합니다.')
        if not any(c.isupper() for c in v):
            raise ValueError('비밀번호는 최소 1개의 대문자를 포함해야 합니다.')
        if not any(c.islower() for c in v):
            raise ValueError('비밀번호는 최소 1개의 소문자를 포함해야 합니다.')
        if not any(c.isdigit() for c in v):
            raise ValueError('비밀번호는 최소 1개의 숫자를 포함해야 합니다.')
        return v

class UserUpdate(BaseModel):
    """사용자 정보 수정 스키마"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None

class UserResponse(UserBase):
    """사용자 응답 스키마"""
    id: UUID
    is_active: bool
    email_verified: bool
    phone_verified: bool
    two_factor_enabled: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    """로그인 요청 스키마"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """토큰 응답 스키마"""
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    """토큰 데이터 스키마"""
    user_id: Optional[str] = None

class PasswordResetRequest(BaseModel):
    """비밀번호 재설정 요청 스키마"""
    email: EmailStr

class PasswordReset(BaseModel):
    """비밀번호 재설정 스키마"""
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('비밀번호는 최소 8자 이상이어야 합니다.')
        if not any(c.isupper() for c in v):
            raise ValueError('비밀번호는 최소 1개의 대문자를 포함해야 합니다.')
        if not any(c.islower() for c in v):
            raise ValueError('비밀번호는 최소 1개의 소문자를 포함해야 합니다.')
        if not any(c.isdigit() for c in v):
            raise ValueError('비밀번호는 최소 1개의 숫자를 포함해야 합니다.')
        return v

class EmailVerification(BaseModel):
    """이메일 인증 스키마"""
    token: str
