"""
보안 관련 유틸리티 함수
"""

from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from app.core.config import settings

# 비밀번호 해싱 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """JWT 리프레시 토큰 생성"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """JWT 토큰 검증"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """비밀번호 해싱"""
    return pwd_context.hash(password)

def generate_verification_code() -> str:
    """6자리 인증 코드 생성"""
    import random
    return str(random.randint(100000, 999999))

def generate_api_key() -> str:
    """API 키 생성"""
    import secrets
    return secrets.token_urlsafe(32)

def validate_password_strength(password: str) -> dict:
    """비밀번호 강도 검증"""
    result = {
        "is_valid": True,
        "errors": []
    }
    
    if len(password) < 8:
        result["is_valid"] = False
        result["errors"].append("비밀번호는 최소 8자 이상이어야 합니다.")
    
    if not any(c.isupper() for c in password):
        result["is_valid"] = False
        result["errors"].append("비밀번호는 최소 1개의 대문자를 포함해야 합니다.")
    
    if not any(c.islower() for c in password):
        result["is_valid"] = False
        result["errors"].append("비밀번호는 최소 1개의 소문자를 포함해야 합니다.")
    
    if not any(c.isdigit() for c in password):
        result["is_valid"] = False
        result["errors"].append("비밀번호는 최소 1개의 숫자를 포함해야 합니다.")
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        result["is_valid"] = False
        result["errors"].append("비밀번호는 최소 1개의 특수문자를 포함해야 합니다.")
    
    return result
