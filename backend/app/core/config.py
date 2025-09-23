"""
Phase 2 설정 관리 모듈
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 기본 설정
    APP_NAME: str = "Crypto Trading Subscription Service"
    VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_HOSTS: List[str] = ["*"]
    FRONTEND_URL: str = "http://localhost:3000"
    
    # 데이터베이스 설정
    DATABASE_URL: str = "postgresql://user:password@postgres:5432/crypto_trading"
    REDIS_URL: str = "redis://redis:6379"
    
    # JWT 설정
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Stripe 설정
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    # 이메일 설정
    SENDGRID_API_KEY: str = ""
    FROM_EMAIL: str = "noreply@crypto-trading.com"
    
    # SMS 설정
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    # Binance API 설정
    BINANCE_API_KEY: str = ""
    BINANCE_SECRET_KEY: str = ""
    BINANCE_TESTNET: bool = True
    
    # 로깅 설정
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # 보안 설정
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # 구독 플랜 설정
    SUBSCRIPTION_PLANS: dict = {
        "basic": {
            "name": "Basic",
            "price_monthly": 29,
            "price_yearly": 290,
            "features": ["basic_strategies", "email_support", "basic_dashboard"]
        },
        "premium": {
            "name": "Premium", 
            "price_monthly": 79,
            "price_yearly": 790,
            "features": ["all_strategies", "ai_insights", "priority_support", "advanced_dashboard"]
        },
        "pro": {
            "name": "Pro",
            "price_monthly": 199,
            "price_yearly": 1990,
            "features": ["all_strategies", "custom_ai", "dedicated_support", "api_access", "custom_dashboard"]
        }
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 전역 설정 인스턴스
settings = Settings()

# 환경별 설정 오버라이드
if settings.ENVIRONMENT == "production":
    settings.DEBUG = False
    settings.LOG_LEVEL = "WARNING"
elif settings.ENVIRONMENT == "staging":
    settings.DEBUG = False
    settings.LOG_LEVEL = "INFO"
