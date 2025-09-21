# 헬스체크 및 모니터링
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
import asyncio
import time
import psutil
import os
from datetime import datetime, timedelta
import structlog

from app.core.database import get_db
from app.services.cache_service import cache_service
from app.services.ai_service import ai_service

# 로거 설정
logger = structlog.get_logger()

router = APIRouter()

class HealthChecker:
    """헬스체크 클래스"""
    
    def __init__(self):
        self.start_time = time.time()
        self.checks = {
            "database": self._check_database,
            "redis": self._check_redis,
            "ai_models": self._check_ai_models,
            "memory": self._check_memory,
            "disk": self._check_disk,
            "cpu": self._check_cpu
        }
    
    async def _check_database(self, db: AsyncSession) -> Dict[str, Any]:
        """데이터베이스 상태 확인"""
        try:
            # 간단한 쿼리 실행
            await db.execute("SELECT 1")
            
            return {
                "status": "healthy",
                "response_time": 0,
                "details": "Database connection successful"
            }
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "response_time": 0,
                "details": f"Database connection failed: {str(e)}"
            }
    
    async def _check_redis(self) -> Dict[str, Any]:
        """Redis 상태 확인"""
        try:
            start_time = time.time()
            
            # Redis 연결 테스트
            await cache_service.set("health_check", "test", ttl=10)
            result = await cache_service.get("health_check")
            
            response_time = (time.time() - start_time) * 1000
            
            if result == "test":
                return {
                    "status": "healthy",
                    "response_time": response_time,
                    "details": "Redis connection successful"
                }
            else:
                return {
                    "status": "unhealthy",
                    "response_time": response_time,
                    "details": "Redis data retrieval failed"
                }
        except Exception as e:
            logger.error("Redis health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "response_time": 0,
                "details": f"Redis connection failed: {str(e)}"
            }
    
    async def _check_ai_models(self) -> Dict[str, Any]:
        """AI 모델 상태 확인"""
        try:
            start_time = time.time()
            
            # AI 모델 상태 확인
            market_detector_healthy = ai_service.market_regime_detector.is_trained
            strategy_recommender_healthy = ai_service.strategy_recommender.is_trained
            risk_assessor_healthy = ai_service.risk_assessor.is_trained
            
            response_time = (time.time() - start_time) * 1000
            
            if market_detector_healthy and strategy_recommender_healthy and risk_assessor_healthy:
                return {
                    "status": "healthy",
                    "response_time": response_time,
                    "details": "All AI models are loaded and ready"
                }
            else:
                return {
                    "status": "degraded",
                    "response_time": response_time,
                    "details": "Some AI models are not loaded"
                }
        except Exception as e:
            logger.error("AI models health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "response_time": 0,
                "details": f"AI models check failed: {str(e)}"
            }
    
    async def _check_memory(self) -> Dict[str, Any]:
        """메모리 사용량 확인"""
        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_usage_mb = memory_info.rss / 1024 / 1024
            
            # 메모리 사용량이 1GB를 초과하면 경고
            if memory_usage_mb > 1024:
                status = "degraded"
                details = f"High memory usage: {memory_usage_mb:.2f}MB"
            else:
                status = "healthy"
                details = f"Memory usage: {memory_usage_mb:.2f}MB"
            
            return {
                "status": status,
                "response_time": 0,
                "details": details,
                "memory_usage_mb": memory_usage_mb
            }
        except Exception as e:
            logger.error("Memory health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "response_time": 0,
                "details": f"Memory check failed: {str(e)}"
            }
    
    async def _check_disk(self) -> Dict[str, Any]:
        """디스크 사용량 확인"""
        try:
            disk_usage = psutil.disk_usage('/')
            disk_percent = (disk_usage.used / disk_usage.total) * 100
            
            # 디스크 사용량이 90%를 초과하면 경고
            if disk_percent > 90:
                status = "degraded"
                details = f"High disk usage: {disk_percent:.1f}%"
            else:
                status = "healthy"
                details = f"Disk usage: {disk_percent:.1f}%"
            
            return {
                "status": status,
                "response_time": 0,
                "details": details,
                "disk_percent": disk_percent
            }
        except Exception as e:
            logger.error("Disk health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "response_time": 0,
                "details": f"Disk check failed: {str(e)}"
            }
    
    async def _check_cpu(self) -> Dict[str, Any]:
        """CPU 사용량 확인"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # CPU 사용량이 80%를 초과하면 경고
            if cpu_percent > 80:
                status = "degraded"
                details = f"High CPU usage: {cpu_percent:.1f}%"
            else:
                status = "healthy"
                details = f"CPU usage: {cpu_percent:.1f}%"
            
            return {
                "status": status,
                "response_time": 0,
                "details": details,
                "cpu_percent": cpu_percent
            }
        except Exception as e:
            logger.error("CPU health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "response_time": 0,
                "details": f"CPU check failed: {str(e)}"
            }

# 전역 헬스체커 인스턴스
health_checker = HealthChecker()

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """기본 헬스체크"""
    try:
        # 데이터베이스 연결 확인
        await db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": time.time() - health_checker.start_time,
            "version": "2.0.0"
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )

@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """상세 헬스체크"""
    try:
        results = {}
        overall_status = "healthy"
        
        # 모든 체크 실행
        for check_name, check_func in health_checker.checks.items():
            if check_name == "database":
                result = await check_func(db)
            else:
                result = await check_func()
            
            results[check_name] = result
            
            # 전체 상태 결정
            if result["status"] == "unhealthy":
                overall_status = "unhealthy"
            elif result["status"] == "degraded" and overall_status == "healthy":
                overall_status = "degraded"
        
        # 응답 시간 계산
        total_response_time = sum(
            result.get("response_time", 0) for result in results.values()
        )
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": time.time() - health_checker.start_time,
            "version": "2.0.0",
            "response_time_ms": total_response_time,
            "checks": results
        }
    except Exception as e:
        logger.error("Detailed health check failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )

@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """준비 상태 확인 (Kubernetes readiness probe)"""
    try:
        # 필수 서비스만 확인
        essential_checks = ["database", "redis"]
        
        for check_name in essential_checks:
            check_func = health_checker.checks[check_name]
            if check_name == "database":
                result = await check_func(db)
            else:
                result = await check_func()
            
            if result["status"] != "healthy":
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Service not ready: {check_name}"
                )
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )

@router.get("/health/live")
async def liveness_check():
    """생존 상태 확인 (Kubernetes liveness probe)"""
    try:
        # 기본적인 애플리케이션 상태만 확인
        return {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": time.time() - health_checker.start_time
        }
    except Exception as e:
        logger.error("Liveness check failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not alive"
        )

@router.get("/metrics")
async def get_metrics():
    """애플리케이션 메트릭"""
    try:
        process = psutil.Process(os.getpid())
        
        # 메모리 메트릭
        memory_info = process.memory_info()
        memory_usage_mb = memory_info.rss / 1024 / 1024
        
        # CPU 메트릭
        cpu_percent = psutil.cpu_percent()
        
        # 디스크 메트릭
        disk_usage = psutil.disk_usage('/')
        disk_percent = (disk_usage.used / disk_usage.total) * 100
        
        # 네트워크 메트릭
        network_io = psutil.net_io_counters()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": time.time() - health_checker.start_time,
            "memory": {
                "usage_mb": memory_usage_mb,
                "percent": process.memory_percent()
            },
            "cpu": {
                "percent": cpu_percent,
                "count": psutil.cpu_count()
            },
            "disk": {
                "usage_percent": disk_percent,
                "free_gb": disk_usage.free / 1024 / 1024 / 1024
            },
            "network": {
                "bytes_sent": network_io.bytes_sent,
                "bytes_recv": network_io.bytes_recv,
                "packets_sent": network_io.packets_sent,
                "packets_recv": network_io.packets_recv
            }
        }
    except Exception as e:
        logger.error("Metrics collection failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to collect metrics"
        )

@router.get("/status")
async def get_status():
    """서비스 상태 요약"""
    try:
        return {
            "service": "crypto-trading-subscription",
            "version": "2.0.0",
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": time.time() - health_checker.start_time,
            "environment": os.getenv("ENVIRONMENT", "development")
        }
    except Exception as e:
        logger.error("Status check failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get status"
        )
