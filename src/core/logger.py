"""
로깅 설정 모듈

시스템 전반의 로깅을 관리하고 설정합니다.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from rich.logging import RichHandler
from rich.console import Console

from .config import get_config


class TradingLogger:
    """거래 시스템 전용 로거"""
    
    def __init__(self, name: str = "trading_system"):
        self.name = name
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """로거 설정"""
        config = get_config()
        logging_config = config.logging
        
        # 기존 핸들러 제거
        self.logger.handlers.clear()
        
        # 로그 레벨 설정
        level = getattr(logging, logging_config.level.upper())
        self.logger.setLevel(level)
        
        # 포맷터 설정
        formatter = logging.Formatter(logging_config.format)
        
        # 콘솔 핸들러 (Rich 사용)
        if logging_config.console_output:
            console = Console()
            console_handler = RichHandler(
                console=console,
                show_time=True,
                show_path=False,
                markup=True
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # 파일 핸들러
        log_file_path = Path(logging_config.file)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path,
            maxBytes=logging_config.max_size_mb * 1024 * 1024,
            backupCount=logging_config.backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # 로그 전파 방지 (중복 출력 방지)
        self.logger.propagate = False
    
    def get_logger(self) -> logging.Logger:
        """로거 인스턴스 반환"""
        return self.logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """로거 인스턴스 반환"""
    if name is None:
        name = "trading_system"
    
    logger = TradingLogger(name)
    return logger.get_logger()


# 전역 로거 인스턴스
main_logger = get_logger("trading_system")
strategy_logger = get_logger("strategy")
data_logger = get_logger("data")
trading_logger = get_logger("trading")
risk_logger = get_logger("risk")


class LogContext:
    """로깅 컨텍스트 매니저"""
    
    def __init__(self, logger: logging.Logger, level: int, message: str, **kwargs):
        self.logger = logger
        self.level = level
        self.message = message
        self.kwargs = kwargs
    
    def __enter__(self):
        self.logger.log(self.level, f"시작: {self.message}", **self.kwargs)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.logger.log(self.level, f"완료: {self.message}", **self.kwargs)
        else:
            self.logger.error(f"오류 발생: {self.message} - {exc_val}", **self.kwargs)


def log_function_call(logger: logging.Logger, level: int = logging.INFO):
    """함수 호출 로깅 데코레이터"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.log(level, f"함수 호출: {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.log(level, f"함수 완료: {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"함수 오류: {func.__name__} - {e}")
                raise
        return wrapper
    return decorator


def log_trade_decision(logger: logging.Logger, decision: str, **kwargs):
    """거래 결정 로깅"""
    logger.info(f"거래 결정: {decision}", extra=kwargs)


def log_risk_event(logger: logging.Logger, event: str, **kwargs):
    """리스크 이벤트 로깅"""
    logger.warning(f"리스크 이벤트: {event}", extra=kwargs)


def log_system_event(logger: logging.Logger, event: str, **kwargs):
    """시스템 이벤트 로깅"""
    logger.info(f"시스템 이벤트: {event}", extra=kwargs)
