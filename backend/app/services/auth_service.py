"""
인증 서비스 클래스
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import secrets
import hashlib

from app.core.config import settings
from app.models.user import User, UserSocialLogin
from app.schemas.auth import UserCreate, UserUpdate
from app.utils.email import send_verification_email, send_password_reset_email

# 비밀번호 해싱 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """인증 서비스 클래스"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user_data: UserCreate) -> User:
        """사용자 생성"""
        # 비밀번호 해싱
        hashed_password = pwd_context.hash(user_data.password)
        
        # 사용자 생성
        user = User(
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            country=user_data.country,
            timezone=user_data.timezone
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        # 이메일 인증 토큰 생성 및 전송
        verification_token = self._generate_verification_token(user.id)
        await send_verification_email(user.email, verification_token)
        
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """ID로 사용자 조회"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """사용자 인증"""
        user = await self.get_user_by_email(email)
        if not user or not user.password_hash:
            return None
        
        if not pwd_context.verify(password, user.password_hash):
            return None
        
        # 마지막 로그인 시간 업데이트
        user.last_login = datetime.utcnow()
        await self.db.commit()
        
        return user
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """사용자 정보 수정"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        # 업데이트할 필드만 수정
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """비밀번호 변경"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        # 기존 비밀번호 확인
        if not pwd_context.verify(old_password, user.password_hash):
            return False
        
        # 새 비밀번호 해싱 및 저장
        user.password_hash = pwd_context.hash(new_password)
        await self.db.commit()
        
        return True
    
    async def reset_password(self, token: str, new_password: str) -> bool:
        """비밀번호 재설정"""
        # 토큰 검증 (실제 구현에서는 Redis나 DB에 저장된 토큰과 비교)
        user_id = self._verify_reset_token(token)
        if not user_id:
            return False
        
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        # 새 비밀번호 설정
        user.password_hash = pwd_context.hash(new_password)
        await self.db.commit()
        
        return True
    
    async def verify_email(self, token: str) -> bool:
        """이메일 인증"""
        user_id = self._verify_email_token(token)
        if not user_id:
            return False
        
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.email_verified = True
        await self.db.commit()
        
        return True
    
    async def verify_email_token(self, token: str) -> bool:
        """이메일 인증 토큰 검증"""
        return await self.verify_email(token)
    
    async def send_password_reset_email(self, email: str) -> bool:
        """비밀번호 재설정 이메일 전송"""
        user = await self.get_user_by_email(email)
        if not user:
            return False
        
        reset_token = self._generate_reset_token(user.id)
        await send_password_reset_email(email, reset_token)
        
        return True
    
    def _generate_verification_token(self, user_id: str) -> str:
        """이메일 인증 토큰 생성"""
        payload = {
            "user_id": str(user_id),
            "type": "email_verification",
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    def _generate_reset_token(self, user_id: str) -> str:
        """비밀번호 재설정 토큰 생성"""
        payload = {
            "user_id": str(user_id),
            "type": "password_reset",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    def _verify_email_token(self, token: str) -> Optional[str]:
        """이메일 인증 토큰 검증"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get("type") != "email_verification":
                return None
            return payload.get("user_id")
        except JWTError:
            return None
    
    def _verify_reset_token(self, token: str) -> Optional[str]:
        """비밀번호 재설정 토큰 검증"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get("type") != "password_reset":
                return None
            return payload.get("user_id")
        except JWTError:
            return None
    
    async def get_user_from_token(self, token: str) -> Optional[User]:
        """토큰에서 사용자 정보 추출"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                return None
            return await self.get_user_by_id(user_id)
        except JWTError:
            return None
