"""
모니터링 미들웨어
"""

import time
import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST

# Prometheus 메트릭 정의
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'http_active_connections',
    'Number of active HTTP connections'
)

DATABASE_CONNECTIONS = Gauge(
    'database_connections_active',
    'Number of active database connections'
)

class MonitoringMiddleware(BaseHTTPMiddleware):
    """모니터링 미들웨어"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = structlog.get_logger()
    
    async def dispatch(self, request: Request, call_next):
        """요청 처리 및 메트릭 수집"""
        start_time = time.time()
        
        # 활성 연결 수 증가
        ACTIVE_CONNECTIONS.inc()
        
        try:
            # 요청 처리
            response = await call_next(request)
            
            # 메트릭 수집
            duration = time.time() - start_time
            method = request.method
            endpoint = request.url.path
            status_code = response.status_code
            
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()
            
            REQUEST_DURATION.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            # 로깅
            self.logger.info(
                "HTTP request processed",
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                duration=duration
            )
            
            return response
            
        except Exception as e:
            # 에러 메트릭 수집
            duration = time.time() - start_time
            method = request.method
            endpoint = request.url.path
            
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status_code=500
            ).inc()
            
            REQUEST_DURATION.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            # 에러 로깅
            self.logger.error(
                "HTTP request failed",
                method=method,
                endpoint=endpoint,
                error=str(e),
                duration=duration
            )
            
            raise
            
        finally:
            # 활성 연결 수 감소
            ACTIVE_CONNECTIONS.dec()

class PrometheusMetrics:
    """Prometheus 메트릭 관리 클래스"""
    
    @staticmethod
    def get_metrics():
        """메트릭 데이터 반환"""
        return generate_latest()
    
    @staticmethod
    def get_content_type():
        """Content-Type 반환"""
        return CONTENT_TYPE_LATEST
    
    @staticmethod
    def update_database_connections(count: int):
        """데이터베이스 연결 수 업데이트"""
        DATABASE_CONNECTIONS.set(count)
