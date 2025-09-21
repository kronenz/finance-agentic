# 구독 관련 Pydantic 스키마
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class SubscriptionStatus(str, Enum):
    """구독 상태 열거형"""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    PENDING = "pending"

class SubscriptionPlanResponse(BaseModel):
    """구독 플랜 응답 스키마"""
    id: str
    name: str
    description: str
    price: float
    currency: str = "USD"
    billing_cycle: str  # monthly, yearly
    features: List[str]
    max_trades_per_day: int
    max_portfolio_value: float
    is_active: bool = True
    
    class Config:
        from_attributes = True

class SubscriptionCreate(BaseModel):
    """구독 생성 요청 스키마"""
    plan_id: str = Field(..., description="구독 플랜 ID")
    payment_method_id: str = Field(..., description="결제 방법 ID")
    billing_cycle: str = Field(..., description="결제 주기 (monthly, yearly)")
    
    @validator('billing_cycle')
    def validate_billing_cycle(cls, v):
        if v not in ['monthly', 'yearly']:
            raise ValueError('billing_cycle must be monthly or yearly')
        return v

class SubscriptionUpdate(BaseModel):
    """구독 업데이트 요청 스키마"""
    plan_id: Optional[str] = None
    payment_method_id: Optional[str] = None
    billing_cycle: Optional[str] = None
    
    @validator('billing_cycle')
    def validate_billing_cycle(cls, v):
        if v is not None and v not in ['monthly', 'yearly']:
            raise ValueError('billing_cycle must be monthly or yearly')
        return v

class SubscriptionResponse(BaseModel):
    """구독 응답 스키마"""
    id: str
    user_id: str
    plan_id: str
    plan_name: str
    status: SubscriptionStatus
    start_date: datetime
    end_date: Optional[datetime]
    billing_cycle: str
    price: float
    currency: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SubscriptionHistoryResponse(BaseModel):
    """구독 이력 응답 스키마"""
    id: str
    subscription_id: str
    action: str  # created, updated, cancelled, reactivated, expired
    old_status: Optional[SubscriptionStatus]
    new_status: SubscriptionStatus
    description: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class SubscriptionStatsResponse(BaseModel):
    """구독 통계 응답 스키마"""
    total_subscriptions: int
    active_subscriptions: int
    cancelled_subscriptions: int
    expired_subscriptions: int
    monthly_revenue: float
    yearly_revenue: float
    most_popular_plan: str
    average_subscription_duration: int  # days

class PaymentMethodResponse(BaseModel):
    """결제 방법 응답 스키마"""
    id: str
    user_id: str
    stripe_payment_method_id: str
    card_last_four: str
    card_brand: str
    card_exp_month: int
    card_exp_year: int
    is_default: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class PaymentMethodCreate(BaseModel):
    """결제 방법 생성 요청 스키마"""
    stripe_payment_method_id: str = Field(..., description="Stripe 결제 방법 ID")
    is_default: bool = False

class BillingInfoResponse(BaseModel):
    """청구 정보 응답 스키마"""
    subscription: SubscriptionResponse
    next_billing_date: Optional[datetime]
    amount_due: float
    currency: str
    payment_method: Optional[PaymentMethodResponse]
    billing_address: Optional[dict]
    
class UsageStatsResponse(BaseModel):
    """사용량 통계 응답 스키마"""
    trades_used: int
    trades_limit: int
    portfolio_value: float
    portfolio_limit: float
    api_calls_used: int
    api_calls_limit: int
    storage_used: float  # MB
    storage_limit: float  # MB
