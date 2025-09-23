"""
로깅 시스템 설정
Crypto Trading Subscription Service
"""

import structlog
import logging
import sys
from typing import Any, Dict
from datetime import datetime
import json

def setup_logging(environment: str = "development") -> None:
    """로깅 시스템 설정"""
    
    # 기본 로깅 설정
    logging.basicConfig(
        level=logging.INFO if environment == "production" else logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
    
    # structlog 설정
    if environment == "production":
        # 프로덕션 환경: JSON 형식 로그
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    else:
        # 개발 환경: 컬러풀한 콘솔 로그
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.dev.ConsoleRenderer(colors=True)
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

class RequestLogger:
    """요청 로깅 클래스"""
    
    def __init__(self):
        self.logger = structlog.get_logger("request")
    
    def log_request(self, method: str, path: str, status_code: int, 
                   response_time: float, user_id: str = None, **kwargs):
        """요청 로그 기록"""
        self.logger.info(
            "HTTP Request",
            method=method,
            path=path,
            status_code=status_code,
            response_time_ms=round(response_time * 1000, 2),
            user_id=user_id,
            **kwargs
        )
    
    def log_error(self, method: str, path: str, error: str, 
                 user_id: str = None, **kwargs):
        """에러 로그 기록"""
        self.logger.error(
            "HTTP Error",
            method=method,
            path=path,
            error=error,
            user_id=user_id,
            **kwargs
        )

class BusinessLogger:
    """비즈니스 로직 로깅 클래스"""
    
    def __init__(self):
        self.logger = structlog.get_logger("business")
    
    def log_user_action(self, action: str, user_id: str, **kwargs):
        """사용자 액션 로그"""
        self.logger.info(
            "User Action",
            action=action,
            user_id=user_id,
            timestamp=datetime.utcnow().isoformat(),
            **kwargs
        )
    
    def log_subscription_event(self, event: str, user_id: str, 
                             subscription_id: str = None, **kwargs):
        """구독 이벤트 로그"""
        self.logger.info(
            "Subscription Event",
            event=event,
            user_id=user_id,
            subscription_id=subscription_id,
            timestamp=datetime.utcnow().isoformat(),
            **kwargs
        )
    
    def log_ai_prediction(self, prediction_type: str, user_id: str, 
                         confidence: float, **kwargs):
        """AI 예측 로그"""
        self.logger.info(
            "AI Prediction",
            prediction_type=prediction_type,
            user_id=user_id,
            confidence=confidence,
            timestamp=datetime.utcnow().isoformat(),
            **kwargs
        )

class SecurityLogger:
    """보안 로깅 클래스"""
    
    def __init__(self):
        self.logger = structlog.get_logger("security")
    
    def log_auth_attempt(self, email: str, success: bool, ip_address: str = None):
        """인증 시도 로그"""
        self.logger.info(
            "Authentication Attempt",
            email=email,
            success=success,
            ip_address=ip_address,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def log_rate_limit(self, ip_address: str, endpoint: str, limit: int):
        """Rate Limiting 로그"""
        self.logger.warning(
            "Rate Limit Exceeded",
            ip_address=ip_address,
            endpoint=endpoint,
            limit=limit,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def log_suspicious_activity(self, activity: str, ip_address: str, 
                               user_id: str = None, **kwargs):
        """의심스러운 활동 로그"""
        self.logger.warning(
            "Suspicious Activity",
            activity=activity,
            ip_address=ip_address,
            user_id=user_id,
            timestamp=datetime.utcnow().isoformat(),
            **kwargs
        )

# 전역 로거 인스턴스
request_logger = RequestLogger()
business_logger = BusinessLogger()
security_logger = SecurityLogger()

def get_logger(name: str) -> structlog.BoundLogger:
    """로거 인스턴스 반환"""
    return structlog.get_logger(name)
