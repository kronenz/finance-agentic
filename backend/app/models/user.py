"""
사용자 관련 데이터베이스 모델
"""

from sqlalchemy import Column, String, Boolean, DateTime, UUID, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class User(Base):
    """사용자 모델"""
    __tablename__ = "users"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    country = Column(String(2), nullable=True)  # ISO country code
    timezone = Column(String(50), default='UTC')
    
    # 상태 플래그
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)
    
    # 메타데이터
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    social_logins = relationship("UserSocialLogin", back_populates="user", cascade="all, delete-orphan")

class UserSocialLogin(Base):
    """사용자 소셜 로그인 모델"""
    __tablename__ = "user_social_logins"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    provider = Column(String(50), nullable=False)  # google, apple, github
    provider_id = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    user = relationship("User", back_populates="social_logins")
    
    __table_args__ = (
        UniqueConstraint('provider', 'provider_id', name='uq_provider_id'),
    )

class UserProfile(Base):
    """사용자 프로필 확장 모델"""
    __tablename__ = "user_profiles"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    
    # 거래 관련 설정
    risk_tolerance = Column(String(20), default='medium')  # low, medium, high
    trading_experience = Column(String(20), default='beginner')  # beginner, intermediate, advanced
    preferred_strategies = Column(JSONB, default=list)
    
    # 개인화 설정
    notification_preferences = Column(JSONB, default=dict)
    dashboard_layout = Column(JSONB, default=dict)
    theme_preference = Column(String(20), default='light')  # light, dark, auto
    
    # 메타데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계
    user = relationship("User", backref="profile")
