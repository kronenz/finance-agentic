"""
JWT 토큰 처리 및 관리
"""

from jose import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# 비밀번호 해싱 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class JWTHandler:
    """JWT 토큰 생성, 검증, 갱신을 담당하는 클래스"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """액세스 토큰 생성"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        logger.info(f"Access token created for user: {data.get('sub', 'unknown')}")
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """리프레시 토큰 생성"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        logger.info(f"Refresh token created for user: {data.get('sub', 'unknown')}")
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str) -> Optional[Dict[str, Any]]:
        """토큰 검증"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 토큰 타입 검증
            if payload.get("type") != token_type:
                logger.warning(f"Invalid token type: expected {token_type}, got {payload.get('type')}")
                return None
            
            # 만료 시간 검증
            if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
                logger.warning("Token has expired")
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.JWTError as e:
            logger.error(f"JWT error: {e}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """리프레시 토큰을 사용하여 새로운 액세스 토큰 생성"""
        payload = self.verify_token(refresh_token, "refresh")
        if not payload:
            return None
        
        # 새로운 액세스 토큰 생성
        new_data = {
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role"),
            "permissions": payload.get("permissions", [])
        }
        
        return self.create_access_token(new_data)
    
    def hash_password(self, password: str) -> str:
        """비밀번호 해싱"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """비밀번호 검증"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_token_payload(self, token: str) -> Optional[Dict[str, Any]]:
        """토큰 페이로드 추출 (검증 없이)"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_exp": False})
            return payload
        except jwt.JWTError:
            return None
