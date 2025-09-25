# 로깅 시스템 설정
import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any
import structlog
from pythonjsonlogger import jsonlogger

class LoggingConfig:
    """로깅 설정 관리자"""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.log_level = "DEBUG" if environment == "development" else "INFO"
        self.log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.json_format = "%(asctime)s %(name)s %(levelname)s %(message)s"
    
    def get_logging_config(self) -> Dict[str, Any]:
        """로깅 설정 반환"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": self.log_format,
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                },
                "json": {
                    "()": jsonlogger.JsonFormatter,
                    "format": self.json_format,
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                },
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": self.log_level,
                    "formatter": "standard" if self.environment == "development" else "json",
                    "stream": sys.stdout
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": self.log_level,
                    "formatter": "json",
                    "filename": "logs/application.log",
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                    "encoding": "utf8"
                },
                "error_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "ERROR",
                    "formatter": "detailed",
                    "filename": "logs/error.log",
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                    "encoding": "utf8"
                },
                "access_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "INFO",
                    "formatter": "json",
                    "filename": "logs/access.log",
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                    "encoding": "utf8"
                },
                "audit_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "INFO",
                    "formatter": "json",
                    "filename": "logs/audit.log",
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 10,
                    "encoding": "utf8"
                }
            },
            "loggers": {
                "": {  # root logger
                    "handlers": ["console", "file"],
                    "level": self.log_level,
                    "propagate": False
                },
                "uvicorn": {
                    "handlers": ["console", "file"],
                    "level": "INFO",
                    "propagate": False
                },
                "uvicorn.access": {
                    "handlers": ["access_file"],
                    "level": "INFO",
                    "propagate": False
                },
                "uvicorn.error": {
                    "handlers": ["error_file"],
                    "level": "ERROR",
                    "propagate": False
                },
                "finance": {
                    "handlers": ["console", "file"],
                    "level": self.log_level,
                    "propagate": False
                },
                "finance.auth": {
                    "handlers": ["console", "file", "audit_file"],
                    "level": "INFO",
                    "propagate": False
                },
                "finance.trading": {
                    "handlers": ["console", "file", "audit_file"],
                    "level": "INFO",
                    "propagate": False
                },
                "finance.ai": {
                    "handlers": ["console", "file"],
                    "level": self.log_level,
                    "propagate": False
                },
                "finance.monitoring": {
                    "handlers": ["console", "file"],
                    "level": "INFO",
                    "propagate": False
                },
                "sqlalchemy": {
                    "handlers": ["file"],
                    "level": "WARNING",
                    "propagate": False
                },
                "redis": {
                    "handlers": ["file"],
                    "level": "WARNING",
                    "propagate": False
                }
            }
        }
    
    def setup_structlog(self):
        """structlog 설정"""
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
                structlog.processors.JSONRenderer() if self.environment != "development" else structlog.dev.ConsoleRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

def setup_logging(environment: str = "development"):
    """로깅 시스템 초기화"""
    # 로그 디렉토리 생성
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 로깅 설정 적용
    config = LoggingConfig(environment)
    logging_config = config.get_logging_config()
    logging.config.dictConfig(logging_config)
    
    # structlog 설정
    config.setup_structlog()
    
    # 로깅 설정 완료 로그
    logger = structlog.get_logger()
    logger.info("Logging system initialized", environment=environment)

class AuditLogger:
    """감사 로그 전용 로거"""
    
    def __init__(self):
        self.logger = structlog.get_logger("finance.audit")
    
    def log_user_action(self, user_id: str, action: str, resource: str, details: Dict[str, Any] = None):
        """사용자 액션 감사 로그"""
        self.logger.info(
            "User action",
            user_id=user_id,
            action=action,
            resource=resource,
            details=details or {}
        )
    
    def log_system_event(self, event_type: str, component: str, details: Dict[str, Any] = None):
        """시스템 이벤트 감사 로그"""
        self.logger.info(
            "System event",
            event_type=event_type,
            component=component,
            details=details or {}
        )
    
    def log_security_event(self, event_type: str, severity: str, details: Dict[str, Any] = None):
        """보안 이벤트 감사 로그"""
        self.logger.warning(
            "Security event",
            event_type=event_type,
            severity=severity,
            details=details or {}
        )
    
    def log_trading_event(self, event_type: str, user_id: str, symbol: str, details: Dict[str, Any] = None):
        """거래 이벤트 감사 로그"""
        self.logger.info(
            "Trading event",
            event_type=event_type,
            user_id=user_id,
            symbol=symbol,
            details=details or {}
        )

# 전역 감사 로거 인스턴스
audit_logger = AuditLogger()

class PerformanceLogger:
    """성능 로그 전용 로거"""
    
    def __init__(self):
        self.logger = structlog.get_logger("finance.performance")
    
    def log_api_request(self, method: str, endpoint: str, status_code: int, 
                       response_time: float, user_id: str = None):
        """API 요청 성능 로그"""
        self.logger.info(
            "API request",
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            response_time_ms=response_time,
            user_id=user_id
        )
    
    def log_database_query(self, query_type: str, table: str, duration: float, 
                          rows_affected: int = None):
        """데이터베이스 쿼리 성능 로그"""
        self.logger.info(
            "Database query",
            query_type=query_type,
            table=table,
            duration_ms=duration,
            rows_affected=rows_affected
        )
    
    def log_cache_operation(self, operation: str, key: str, hit: bool, duration: float):
        """캐시 작업 성능 로그"""
        self.logger.info(
            "Cache operation",
            operation=operation,
            key=key,
            hit=hit,
            duration_ms=duration
        )
    
    def log_ai_processing(self, agent_type: str, message_type: str, duration: float, 
                         success: bool):
        """AI 처리 성능 로그"""
        self.logger.info(
            "AI processing",
            agent_type=agent_type,
            message_type=message_type,
            duration_ms=duration,
            success=success
        )

# 전역 성능 로거 인스턴스
performance_logger = PerformanceLogger()
