"""
에러 처리 및 로깅 유틸리티
"""

import logging
import traceback
import functools
from typing import Any, Callable, Dict, Optional, Union
from datetime import datetime
import json
from enum import Enum

logger = logging.getLogger(__name__)

class ErrorLevel(Enum):
    """에러 레벨"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ErrorCode(Enum):
    """에러 코드"""
    # 일반 에러
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    
    # 데이터베이스 에러
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    DATABASE_QUERY_ERROR = "DATABASE_QUERY_ERROR"
    DATABASE_TRANSACTION_ERROR = "DATABASE_TRANSACTION_ERROR"
    
    # API 에러
    API_REQUEST_ERROR = "API_REQUEST_ERROR"
    API_RESPONSE_ERROR = "API_RESPONSE_ERROR"
    API_TIMEOUT_ERROR = "API_TIMEOUT_ERROR"
    
    # AI/ML 에러
    MODEL_LOADING_ERROR = "MODEL_LOADING_ERROR"
    MODEL_PREDICTION_ERROR = "MODEL_PREDICTION_ERROR"
    MODEL_TRAINING_ERROR = "MODEL_TRAINING_ERROR"
    
    # 거래 에러
    TRADING_EXECUTION_ERROR = "TRADING_EXECUTION_ERROR"
    TRADING_VALIDATION_ERROR = "TRADING_VALIDATION_ERROR"
    TRADING_RISK_ERROR = "TRADING_RISK_ERROR"
    
    # 시스템 에러
    SYSTEM_RESOURCE_ERROR = "SYSTEM_RESOURCE_ERROR"
    SYSTEM_CONFIGURATION_ERROR = "SYSTEM_CONFIGURATION_ERROR"
    SYSTEM_MAINTENANCE_ERROR = "SYSTEM_MAINTENANCE_ERROR"

class TradingError(Exception):
    """거래 관련 에러"""
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.TRADING_EXECUTION_ERROR, 
                 details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class AIAgentError(Exception):
    """AI 에이전트 관련 에러"""
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.MODEL_PREDICTION_ERROR,
                 details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class DatabaseError(Exception):
    """데이터베이스 관련 에러"""
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.DATABASE_QUERY_ERROR,
                 details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class ErrorHandler:
    """에러 처리 클래스"""
    
    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.error_history: list = []
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None,
                    level: ErrorLevel = ErrorLevel.ERROR) -> Dict[str, Any]:
        """에러 처리 및 로깅"""
        error_info = self._extract_error_info(error, context)
        
        # 에러 카운트 증가
        error_key = f"{error_info['error_code']}:{error_info['error_type']}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # 에러 히스토리에 추가
        self.error_history.append(error_info)
        if len(self.error_history) > 1000:  # 최대 1000개 유지
            self.error_history = self.error_history[-1000:]
        
        # 로깅
        self._log_error(error_info, level)
        
        return error_info
    
    def _extract_error_info(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """에러 정보 추출"""
        error_info = {
            'timestamp': datetime.utcnow().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'error_code': getattr(error, 'error_code', ErrorCode.UNKNOWN_ERROR).value,
            'details': getattr(error, 'details', {}),
            'context': context or {},
            'traceback': traceback.format_exc(),
            'stack_trace': traceback.format_stack()
        }
        
        return error_info
    
    def _log_error(self, error_info: Dict[str, Any], level: ErrorLevel):
        """에러 로깅"""
        log_message = {
            'error_code': error_info['error_code'],
            'error_type': error_info['error_type'],
            'error_message': error_info['error_message'],
            'context': error_info['context'],
            'timestamp': error_info['timestamp']
        }
        
        if level == ErrorLevel.DEBUG:
            logger.debug(json.dumps(log_message, indent=2))
        elif level == ErrorLevel.INFO:
            logger.info(json.dumps(log_message, indent=2))
        elif level == ErrorLevel.WARNING:
            logger.warning(json.dumps(log_message, indent=2))
        elif level == ErrorLevel.ERROR:
            logger.error(json.dumps(log_message, indent=2))
        elif level == ErrorLevel.CRITICAL:
            logger.critical(json.dumps(log_message, indent=2))
    
    def get_error_stats(self) -> Dict[str, Any]:
        """에러 통계 조회"""
        return {
            'error_counts': self.error_counts,
            'total_errors': sum(self.error_counts.values()),
            'recent_errors': self.error_history[-10:] if self.error_history else []
        }
    
    def clear_error_history(self):
        """에러 히스토리 초기화"""
        self.error_counts.clear()
        self.error_history.clear()

# 전역 에러 핸들러
error_handler = ErrorHandler()

def handle_errors(error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR, 
                 level: ErrorLevel = ErrorLevel.ERROR,
                 context: Optional[Dict[str, Any]] = None):
    """에러 처리 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_context = context or {}
                error_context.update({
                    'function': func.__name__,
                    'module': func.__module__,
                    'args': str(args)[:200],  # 길이 제한
                    'kwargs': str(kwargs)[:200]
                })
                
                error_info = error_handler.handle_error(e, error_context, level)
                
                # 에러 재발생 (필요한 경우)
                if level in [ErrorLevel.ERROR, ErrorLevel.CRITICAL]:
                    raise
                
                return None
        return wrapper
    return decorator

def handle_async_errors(error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
                       level: ErrorLevel = ErrorLevel.ERROR,
                       context: Optional[Dict[str, Any]] = None):
    """비동기 에러 처리 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_context = context or {}
                error_context.update({
                    'function': func.__name__,
                    'module': func.__module__,
                    'args': str(args)[:200],
                    'kwargs': str(kwargs)[:200]
                })
                
                error_info = error_handler.handle_error(e, error_context, level)
                
                if level in [ErrorLevel.ERROR, ErrorLevel.CRITICAL]:
                    raise
                
                return None
        return wrapper
    return decorator

class RetryConfig:
    """재시도 설정"""
    def __init__(self, max_attempts: int = 3, delay: float = 1.0, 
                 backoff_factor: float = 2.0, max_delay: float = 60.0):
        self.max_attempts = max_attempts
        self.delay = delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay

def retry_on_error(retry_config: RetryConfig = None, 
                  retryable_errors: tuple = (Exception,)):
    """에러 시 재시도 데코레이터"""
    if retry_config is None:
        retry_config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            delay = retry_config.delay
            
            for attempt in range(retry_config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except retryable_errors as e:
                    last_exception = e
                    
                    if attempt == retry_config.max_attempts - 1:
                        # 마지막 시도에서도 실패
                        error_handler.handle_error(e, {
                            'function': func.__name__,
                            'attempt': attempt + 1,
                            'max_attempts': retry_config.max_attempts
                        }, ErrorLevel.ERROR)
                        raise
                    
                    # 재시도 전 대기
                    import time
                    time.sleep(min(delay, retry_config.max_delay))
                    delay *= retry_config.backoff_factor
                    
                    logger.warning(f"Retry {attempt + 1}/{retry_config.max_attempts} for {func.__name__}: {e}")
            
            # 이론적으로 도달하지 않음
            raise last_exception
        return wrapper
    return decorator

def retry_on_async_error(retry_config: RetryConfig = None,
                        retryable_errors: tuple = (Exception,)):
    """비동기 에러 시 재시도 데코레이터"""
    if retry_config is None:
        retry_config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            delay = retry_config.delay
            
            for attempt in range(retry_config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except retryable_errors as e:
                    last_exception = e
                    
                    if attempt == retry_config.max_attempts - 1:
                        error_handler.handle_error(e, {
                            'function': func.__name__,
                            'attempt': attempt + 1,
                            'max_attempts': retry_config.max_attempts
                        }, ErrorLevel.ERROR)
                        raise
                    
                    # 비동기 대기
                    import asyncio
                    await asyncio.sleep(min(delay, retry_config.max_delay))
                    delay *= retry_config.backoff_factor
                    
                    logger.warning(f"Async retry {attempt + 1}/{retry_config.max_attempts} for {func.__name__}: {e}")
            
            raise last_exception
        return wrapper
    return decorator

class CircuitBreaker:
    """서킷 브레이커"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs):
        """서킷 브레이커를 통한 함수 호출"""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """리셋 시도 여부 확인"""
        if self.last_failure_time is None:
            return True
        return (datetime.utcnow().timestamp() - self.last_failure_time) > self.recovery_timeout
    
    def _on_success(self):
        """성공 시 처리"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """실패 시 처리"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow().timestamp()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

def circuit_breaker(failure_threshold: int = 5, recovery_timeout: int = 60):
    """서킷 브레이커 데코레이터"""
    breaker = CircuitBreaker(failure_threshold, recovery_timeout)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator

def log_function_call(level: ErrorLevel = ErrorLevel.DEBUG):
    """함수 호출 로깅 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log_message = {
                'function': func.__name__,
                'module': func.__module__,
                'args_count': len(args),
                'kwargs_count': len(kwargs),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if level == ErrorLevel.DEBUG:
                logger.debug(json.dumps(log_message))
            elif level == ErrorLevel.INFO:
                logger.info(json.dumps(log_message))
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def validate_inputs(**validators):
    """입력 검증 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 함수 시그니처 분석
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # 검증 실행
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not validator(value):
                        raise ValueError(f"Validation failed for parameter '{param_name}' with value '{value}'")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# 일반적인 검증 함수들
def is_positive(value):
    """양수 검증"""
    return isinstance(value, (int, float)) and value > 0

def is_non_negative(value):
    """음이 아닌 수 검증"""
    return isinstance(value, (int, float)) and value >= 0

def is_string(value):
    """문자열 검증"""
    return isinstance(value, str)

def is_not_empty(value):
    """비어있지 않은 값 검증"""
    return value is not None and value != ""

def is_in_range(min_val, max_val):
    """범위 내 값 검증"""
    def validator(value):
        return isinstance(value, (int, float)) and min_val <= value <= max_val
    return validator
