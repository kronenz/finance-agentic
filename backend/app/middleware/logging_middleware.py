"""
로깅 미들웨어
Crypto Trading Subscription Service
"""

import time
import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import request_logger

class LoggingMiddleware(BaseHTTPMiddleware):
    """요청/응답 로깅 미들웨어"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = structlog.get_logger("middleware")
    
    async def dispatch(self, request: Request, call_next):
        """요청 처리 및 로깅"""
        start_time = time.time()
        
        # 요청 정보 추출
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # 사용자 ID 추출 (JWT 토큰에서)
        user_id = None
        if "authorization" in request.headers:
            try:
                # JWT 토큰에서 사용자 ID 추출 (간단한 예시)
                # 실제로는 JWT 토큰을 디코딩해야 함
                user_id = "extracted_from_token"
            except Exception:
                pass
        
        # 요청 로그
        self.logger.info(
            "Request Started",
            method=method,
            path=path,
            client_ip=client_ip,
            user_agent=user_agent,
            user_id=user_id
        )
        
        try:
            # 요청 처리
            response = await call_next(request)
            
            # 응답 시간 계산
            process_time = time.time() - start_time
            
            # 응답 로그
            request_logger.log_request(
                method=method,
                path=path,
                status_code=response.status_code,
                response_time=process_time,
                user_id=user_id,
                client_ip=client_ip,
                user_agent=user_agent
            )
            
            return response
            
        except Exception as e:
            # 에러 로그
            process_time = time.time() - start_time
            
            request_logger.log_error(
                method=method,
                path=path,
                error=str(e),
                user_id=user_id,
                client_ip=client_ip,
                user_agent=user_agent,
                response_time=process_time
            )
            
            raise
