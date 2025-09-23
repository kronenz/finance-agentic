"""
Phase 2 개인형 구독 서비스 - FastAPI 메인 애플리케이션
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn
import structlog

from app.core.config import settings
from app.core.database import engine, Base
from app.core.openapi import custom_openapi
from app.core.logging import setup_logging
from app.middleware.logging_middleware import LoggingMiddleware
from app.api.v1 import auth, subscriptions, ai
from app.monitoring.health_check import router as health_router

# 로깅 시스템 설정
setup_logging(environment=settings.ENVIRONMENT)
logger = structlog.get_logger()

# Rate Limiter 설정
limiter = Limiter(key_func=get_remote_address)

# FastAPI 앱 생성
app = FastAPI(
    title="Crypto Trading Subscription Service",
    description="Phase 2 개인형 구독 서비스 API",
    version="2.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
)

# 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Rate Limiter 설정
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 로깅 미들웨어 추가
app.add_middleware(LoggingMiddleware)


# 데이터베이스 테이블 생성
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    logger.info("Starting Crypto Trading Subscription Service")
    
    # 데이터베이스 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    logger.info("Shutting down Crypto Trading Subscription Service")

# 헬스 체크 엔드포인트
@app.get("/health")
async def health_check():
    """서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": "crypto-trading-subscription",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT
    }

# API 라우터 등록
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(subscriptions.router, prefix="/api/v1/subscriptions", tags=["subscriptions"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"])

# 모니터링 라우터 등록
app.include_router(health_router, tags=["monitoring"])

# 전역 예외 처리
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP 예외 처리"""
    logger.error(
        "HTTP exception occurred",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """일반 예외 처리"""
    logger.error(
        "Unhandled exception occurred",
        error=str(exc),
        path=request.url.path
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )
