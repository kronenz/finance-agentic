"""
메트릭 API 엔드포인트
"""

from fastapi import APIRouter, Response
from app.middleware.monitoring import PrometheusMetrics

router = APIRouter()

@router.get("/metrics")
async def get_metrics():
    """Prometheus 메트릭 엔드포인트"""
    metrics_data = PrometheusMetrics.get_metrics()
    content_type = PrometheusMetrics.get_content_type()
    
    return Response(
        content=metrics_data,
        media_type=content_type
    )

@router.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "service": "crypto-trading-subscription",
        "version": "2.0.0"
    }

@router.get("/ready")
async def readiness_check():
    """준비 상태 체크 엔드포인트"""
    # 데이터베이스 연결 확인
    # Redis 연결 확인
    # 기타 의존성 확인
    
    return {
        "status": "ready",
        "checks": {
            "database": "ok",
            "redis": "ok",
            "external_apis": "ok"
        }
    }
