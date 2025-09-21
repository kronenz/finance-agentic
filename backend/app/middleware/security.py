# 보안 미들웨어
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import hashlib
import hmac
import structlog
from typing import Dict, Set
from datetime import datetime, timedelta
import asyncio

from app.core.config import settings

# 로거 설정
logger = structlog.get_logger()

class SecurityMiddleware(BaseHTTPMiddleware):
    """보안 미들웨어"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.rate_limit_storage: Dict[str, Dict[str, int]] = {}
        self.blocked_ips: Set[str] = set()
        self.suspicious_ips: Set[str] = set()
        self.max_requests_per_minute = 60
        self.max_requests_per_hour = 1000
        self.block_duration_minutes = 60
        
    async def dispatch(self, request: Request, call_next):
        """요청 처리"""
        client_ip = self._get_client_ip(request)
        
        # IP 차단 확인
        if client_ip in self.blocked_ips:
            logger.warning("Blocked IP attempted access", ip=client_ip)
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"message": "Access denied"}
            )
        
        # Rate limiting
        if not await self._check_rate_limit(client_ip):
            logger.warning("Rate limit exceeded", ip=client_ip)
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"message": "Rate limit exceeded"}
            )
        
        # 보안 헤더 추가
        response = await call_next(request)
        
        # 보안 헤더 설정
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        # CORS 헤더 (개발 환경에서만)
        if settings.ENVIRONMENT == "development":
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """클라이언트 IP 주소 추출"""
        # X-Forwarded-For 헤더 확인 (프록시 환경)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # X-Real-IP 헤더 확인
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 직접 연결
        return request.client.host if request.client else "unknown"
    
    async def _check_rate_limit(self, client_ip: str) -> bool:
        """Rate limiting 확인"""
        now = int(time.time())
        minute_key = f"{client_ip}:{now // 60}"
        hour_key = f"{client_ip}:{now // 3600}"
        
        # 분당 요청 수 확인
        if minute_key not in self.rate_limit_storage:
            self.rate_limit_storage[minute_key] = {"count": 0, "timestamp": now}
        
        minute_data = self.rate_limit_storage[minute_key]
        if now - minute_data["timestamp"] > 60:
            minute_data["count"] = 0
            minute_data["timestamp"] = now
        
        minute_data["count"] += 1
        
        if minute_data["count"] > self.max_requests_per_minute:
            await self._handle_suspicious_activity(client_ip)
            return False
        
        # 시간당 요청 수 확인
        if hour_key not in self.rate_limit_storage:
            self.rate_limit_storage[hour_key] = {"count": 0, "timestamp": now}
        
        hour_data = self.rate_limit_storage[hour_key]
        if now - hour_data["timestamp"] > 3600:
            hour_data["count"] = 0
            hour_data["timestamp"] = now
        
        hour_data["count"] += 1
        
        if hour_data["count"] > self.max_requests_per_hour:
            await self._handle_suspicious_activity(client_ip)
            return False
        
        return True
    
    async def _handle_suspicious_activity(self, client_ip: str) -> None:
        """의심스러운 활동 처리"""
        self.suspicious_ips.add(client_ip)
        logger.warning("Suspicious activity detected", ip=client_ip)
        
        # 의심스러운 IP를 일시적으로 차단
        asyncio.create_task(self._temporary_block_ip(client_ip))
    
    async def _temporary_block_ip(self, client_ip: str) -> None:
        """IP 일시 차단"""
        self.blocked_ips.add(client_ip)
        logger.warning("IP temporarily blocked", ip=client_ip)
        
        # 차단 시간 후 해제
        await asyncio.sleep(self.block_duration_minutes * 60)
        self.blocked_ips.discard(client_ip)
        logger.info("IP block lifted", ip=client_ip)

class InputValidationMiddleware(BaseHTTPMiddleware):
    """입력 검증 미들웨어"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.max_content_length = 10 * 1024 * 1024  # 10MB
        self.allowed_content_types = {
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data"
        }
    
    async def dispatch(self, request: Request, call_next):
        """요청 처리"""
        # Content-Length 확인
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_content_length:
            logger.warning("Request too large", content_length=content_length)
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"message": "Request too large"}
            )
        
        # Content-Type 확인
        content_type = request.headers.get("content-type", "")
        if content_type and not any(ct in content_type for ct in self.allowed_content_types):
            logger.warning("Invalid content type", content_type=content_type)
            return JSONResponse(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                content={"message": "Unsupported media type"}
            )
        
        # SQL Injection 패턴 검사
        if await self._check_sql_injection(request):
            logger.warning("SQL injection attempt detected", ip=request.client.host)
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Invalid request"}
            )
        
        # XSS 패턴 검사
        if await self._check_xss(request):
            logger.warning("XSS attempt detected", ip=request.client.host)
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Invalid request"}
            )
        
        return await call_next(request)
    
    async def _check_sql_injection(self, request: Request) -> bool:
        """SQL Injection 패턴 검사"""
        sql_patterns = [
            "union select",
            "drop table",
            "delete from",
            "insert into",
            "update set",
            "exec(",
            "execute(",
            "script>",
            "<script",
            "javascript:",
            "vbscript:",
            "onload=",
            "onerror="
        ]
        
        # URL 파라미터 검사
        for param_name, param_value in request.query_params.items():
            if isinstance(param_value, str):
                for pattern in sql_patterns:
                    if pattern.lower() in param_value.lower():
                        return True
        
        # 요청 본문 검사 (JSON)
        if request.headers.get("content-type", "").startswith("application/json"):
            try:
                body = await request.json()
                if self._check_dict_for_patterns(body, sql_patterns):
                    return True
            except:
                pass
        
        return False
    
    async def _check_xss(self, request: Request) -> bool:
        """XSS 패턴 검사"""
        xss_patterns = [
            "<script",
            "javascript:",
            "vbscript:",
            "onload=",
            "onerror=",
            "onclick=",
            "onmouseover=",
            "onfocus=",
            "onblur=",
            "onchange=",
            "onsubmit=",
            "onreset=",
            "onselect=",
            "onkeydown=",
            "onkeyup=",
            "onkeypress="
        ]
        
        # URL 파라미터 검사
        for param_name, param_value in request.query_params.items():
            if isinstance(param_value, str):
                for pattern in xss_patterns:
                    if pattern.lower() in param_value.lower():
                        return True
        
        return False
    
    def _check_dict_for_patterns(self, data: dict, patterns: list) -> bool:
        """딕셔너리에서 패턴 검사"""
        for key, value in data.items():
            if isinstance(value, str):
                for pattern in patterns:
                    if pattern.lower() in value.lower():
                        return True
            elif isinstance(value, dict):
                if self._check_dict_for_patterns(value, patterns):
                    return True
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        for pattern in patterns:
                            if pattern.lower() in item.lower():
                                return True
                    elif isinstance(item, dict):
                        if self._check_dict_for_patterns(item, patterns):
                            return True
        return False

class CSRFMiddleware(BaseHTTPMiddleware):
    """CSRF 보호 미들웨어"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.secret_key = settings.SECRET_KEY
        self.token_storage: Dict[str, str] = {}
    
    async def dispatch(self, request: Request, call_next):
        """요청 처리"""
        # GET 요청은 CSRF 검사 생략
        if request.method == "GET":
            return await call_next(request)
        
        # CSRF 토큰 검사
        if not await self._validate_csrf_token(request):
            logger.warning("CSRF token validation failed", ip=request.client.host)
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"message": "CSRF token validation failed"}
            )
        
        return await call_next(request)
    
    async def _validate_csrf_token(self, request: Request) -> bool:
        """CSRF 토큰 검증"""
        # CSRF 토큰 추출
        csrf_token = request.headers.get("X-CSRF-Token")
        if not csrf_token:
            return False
        
        # 세션 ID 추출 (실제로는 쿠키에서)
        session_id = request.cookies.get("session_id")
        if not session_id:
            return False
        
        # 토큰 검증
        expected_token = self._generate_csrf_token(session_id)
        return hmac.compare_digest(csrf_token, expected_token)
    
    def _generate_csrf_token(self, session_id: str) -> str:
        """CSRF 토큰 생성"""
        message = f"{session_id}:{int(time.time())}"
        return hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def get_csrf_token(self, session_id: str) -> str:
        """CSRF 토큰 반환"""
        return self._generate_csrf_token(session_id)
