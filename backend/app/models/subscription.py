"""
구독 관련 데이터베이스 모델
"""

from sqlalchemy import Column, String, Boolean, DateTime, UUID, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class SubscriptionPlan(Base):
    """구독 플랜 모델"""
    __tablename__ = "subscription_plans"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)  # basic, premium, pro
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price_monthly = Column(Numeric(10, 2), nullable=False)
    price_yearly = Column(Numeric(10, 2), nullable=False)
    features = Column(JSONB, nullable=True)  # 플랜별 기능 목록
    is_active = Column(Boolean, default=True)
    
    # 메타데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계
    subscriptions = relationship("Subscription", back_populates="plan")

class Subscription(Base):
    """구독 모델"""
    __tablename__ = "subscriptions"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    plan_id = Column(PostgresUUID(as_uuid=True), ForeignKey("subscription_plans.id"))
    
    # 구독 상태
    status = Column(String(20), nullable=False, index=True)  # active, cancelled, expired, past_due
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Stripe 연동
    stripe_subscription_id = Column(String(255), unique=True, nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)
    
    # 무료 체험
    trial_end = Column(DateTime(timezone=True), nullable=True)
    
    # 구독 취소
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)
    
    # 메타데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription", cascade="all, delete-orphan")

class Payment(Base):
    """결제 내역 모델"""
    __tablename__ = "payments"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    subscription_id = Column(PostgresUUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True)
    
    # 결제 정보
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default='USD')
    status = Column(String(20), nullable=False)  # pending, completed, failed, refunded
    
    # Stripe 연동
    stripe_payment_intent_id = Column(String(255), unique=True, nullable=True)
    stripe_charge_id = Column(String(255), nullable=True)
    
    # 결제 방법
    payment_method = Column(String(50), nullable=True)  # card, bank_transfer, etc.
    
    # 메타데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계
    user = relationship("User", backref="payments")
    subscription = relationship("Subscription", back_populates="payments")

class Coupon(Base):
    """쿠폰 모델"""
    __tablename__ = "coupons"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # 할인 설정
    discount_type = Column(String(20), nullable=False)  # percentage, fixed_amount
    discount_value = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default='USD')
    
    # 사용 제한
    max_uses = Column(Integer, nullable=True)
    max_uses_per_user = Column(Integer, default=1)
    used_count = Column(Integer, default=0)
    
    # 유효 기간
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    
    # 상태
    is_active = Column(Boolean, default=True)
    
    # 메타데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
