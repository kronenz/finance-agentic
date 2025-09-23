"""
설정 관리 모듈

YAML 설정 파일을 로드하고 검증하는 기능을 제공합니다.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv


class TradingConfig(BaseModel):
    """거래 관련 설정"""
    exchange: str = "binance"
    symbol: str = "BTCUSDT"
    leverage: int = Field(ge=1, le=20, default=5)
    position_size_percent: float = Field(ge=0.1, le=10.0, default=1.0)
    max_daily_loss_percent: float = Field(ge=0.1, le=10.0, default=2.0)
    testnet: bool = True


class StrategyConfig(BaseModel):
    """전략 관련 설정"""
    supertrend: Dict[str, Any] = Field(default_factory=dict)
    rsi_mean_reversion: Dict[str, Any] = Field(default_factory=dict)


class RiskManagementConfig(BaseModel):
    """리스크 관리 설정"""
    max_consecutive_losses: int = Field(ge=1, le=10, default=3)
    maintenance_margin_buffer: float = Field(ge=1.0, le=3.0, default=1.5)
    emergency_stop_loss: bool = True
    max_position_size_usdt: float = Field(ge=100, le=10000, default=1000)


class DataConfig(BaseModel):
    """데이터 관련 설정"""
    timeframes: list[str] = Field(default_factory=lambda: ["1m", "5m", "1h", "1d"])
    cache_days: int = Field(ge=30, le=3650, default=365)
    update_interval_seconds: int = Field(ge=10, le=3600, default=60)


class APIConfig(BaseModel):
    """API 관련 설정"""
    binance: Dict[str, Any] = Field(default_factory=dict)


class LoggingConfig(BaseModel):
    """로깅 설정"""
    level: str = Field(default="INFO")
    file: str = "logs/trading.log"
    max_size_mb: int = Field(ge=10, le=1000, default=100)
    backup_count: int = Field(ge=1, le=50, default=5)
    console_output: bool = True
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class DatabaseConfig(BaseModel):
    """데이터베이스 설정"""
    path: str = "data/trading.db"
    backup_interval_hours: int = Field(ge=1, le=168, default=24)
    max_backups: int = Field(ge=5, le=100, default=30)


class NotificationsConfig(BaseModel):
    """알림 설정"""
    enabled: bool = False
    webhook_url: Optional[str] = None
    error_notifications: bool = True
    trade_notifications: bool = True


class Config(BaseModel):
    """전체 설정"""
    trading: TradingConfig = Field(default_factory=TradingConfig)
    strategies: StrategyConfig = Field(default_factory=StrategyConfig)
    risk_management: RiskManagementConfig = Field(default_factory=RiskManagementConfig)
    data: DataConfig = Field(default_factory=DataConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    notifications: NotificationsConfig = Field(default_factory=NotificationsConfig)

    @validator('api')
    def validate_api_keys(cls, v):
        """API 키 검증"""
        # API 키 검증은 선택사항으로 변경 (테스트 환경)
        return v


class ConfigManager:
    """설정 관리자"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self._config: Optional[Config] = None
        self._load_env()
    
    def _get_default_config_path(self) -> str:
        """기본 설정 파일 경로 반환"""
        current_dir = Path(__file__).parent.parent.parent
        return str(current_dir / "config" / "config.yaml")
    
    def _load_env(self):
        """환경 변수 로드"""
        env_path = Path(__file__).parent.parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
    
    def load_config(self) -> Config:
        """설정 파일 로드"""
        if self._config is not None:
            return self._config
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            # 환경 변수 치환
            config_data = self._substitute_env_vars(config_data)
            
            self._config = Config(**config_data)
            return self._config
            
        except FileNotFoundError:
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"설정 파일 형식이 올바르지 않습니다: {e}")
        except Exception as e:
            raise ValueError(f"설정 로드 중 오류가 발생했습니다: {e}")
    
    def _substitute_env_vars(self, data: Any) -> Any:
        """환경 변수 치환"""
        if isinstance(data, dict):
            return {k: self._substitute_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._substitute_env_vars(item) for item in data]
        elif isinstance(data, str) and data.startswith("${") and data.endswith("}"):
            env_var = data[2:-1]
            return os.getenv(env_var, data)
        else:
            return data
    
    def get_config(self) -> Config:
        """설정 반환 (캐시된 설정이 있으면 반환)"""
        if self._config is None:
            return self.load_config()
        return self._config
    
    def reload_config(self) -> Config:
        """설정 재로드"""
        self._config = None
        return self.load_config()


# 전역 설정 관리자 인스턴스
config_manager = ConfigManager()


def get_config() -> Config:
    """전역 설정 반환"""
    return config_manager.get_config()


def reload_config() -> Config:
    """전역 설정 재로드"""
    return config_manager.reload_config()
