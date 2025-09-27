from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = "postgresql://user:password@localhost/ai_trading"
    REDIS_URL: str = "redis://localhost:6379"
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI 기반 적응형 암호화폐 거래 시스템"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CONTENT_SECURITY_POLICY: str = "default-src 'self'"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    TRUSTED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # Rate Limiting
    RATE_LIMIT_CALLS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # Session Management
    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_SESSIONS_PER_USER: int = 5
    
    # App Info
    APP_NAME: str = "AI Trading System"
    APP_VERSION: str = "1.0.0"
    
    # AI/ML settings
    MODEL_UPDATE_INTERVAL: int = 3600  # 1 hour
    CONFIDENCE_THRESHOLD: float = 0.7
    
    # Trading settings
    MAX_POSITION_SIZE: float = 10000.0
    RISK_FREE_RATE: float = 0.02
    
    # Monitoring
    LOG_LEVEL: str = "INFO"
    ENABLE_METRICS: bool = True
    
    # Email settings
    SENDGRID_API_KEY: str = "your-sendgrid-api-key"
    FROM_EMAIL: str = "noreply@example.com"
    
    # SMS settings
    TWILIO_ACCOUNT_SID: str = "your-twilio-account-sid"
    TWILIO_AUTH_TOKEN: str = "your-twilio-auth-token"
    TWILIO_PHONE_NUMBER: str = "+1234567890"
    
    # Stripe settings
    STRIPE_SECRET_KEY: str = "sk_test_your_stripe_secret_key"
    STRIPE_PUBLISHABLE_KEY: str = "pk_test_your_stripe_publishable_key"
    STRIPE_WEBHOOK_SECRET: str = "whsec_your_webhook_secret"
    
    # Binance API settings
    BINANCE_API_KEY: str = "your_binance_api_key"
    BINANCE_SECRET_KEY: str = "your_binance_secret_key"
    BINANCE_TESTNET: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()