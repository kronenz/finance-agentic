# 구독 플랜 모델
from sqlalchemy import Column, String, Float, Boolean, Text, Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base

class SubscriptionPlan(Base):
    """구독 플랜 모델"""
    __tablename__ = "subscription_plans"
    
    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    billing_cycle = Column(String(20), nullable=False)  # monthly, yearly
    features = Column(ARRAY(String), nullable=False)
    max_trades_per_day = Column(Integer, nullable=False)
    max_portfolio_value = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<SubscriptionPlan(id='{self.id}', name='{self.name}', price={self.price})>"
