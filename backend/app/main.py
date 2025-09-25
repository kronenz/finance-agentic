from fastapi import FastAPI
from app.api.v1 import trading, analysis, monitoring
from app.auth.main import router as auth_router
from app.core.config import settings
from app.middleware.security import setup_all_middleware

app = FastAPI(
    title="AI 기반 적응형 암호화폐 거래 시스템",
    description="시장 국면 자동 감지 및 전략 동적 전환을 통한 자율적 거래 실행 시스템",
    version="1.0.0"
)

# 모든 미들웨어 설정
setup_all_middleware(app)

# API 라우터 등록
app.include_router(trading.router, prefix="/api/v1/trading", tags=["trading"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["monitoring"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "AI 기반 적응형 암호화폐 거래 시스템 API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)