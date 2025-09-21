"""
기본 전략 클래스

모든 거래 전략의 기본이 되는 추상 클래스입니다.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import pandas as pd

from ..core.logger import get_logger


class TradingSignal:
    """거래 신호 클래스"""
    
    def __init__(self, 
                 signal_type: str,  # 'buy', 'sell', 'hold'
                 strength: float,   # 0.0 ~ 1.0
                 price: float,
                 timestamp: datetime,
                 metadata: Optional[Dict[str, Any]] = None):
        self.signal_type = signal_type
        self.strength = strength
        self.price = price
        self.timestamp = timestamp
        self.metadata = metadata or {}
    
    def __repr__(self):
        return f"TradingSignal({self.signal_type}, {self.strength:.2f}, {self.price:.2f})"


class BaseStrategy(ABC):
    """기본 전략 추상 클래스"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.logger = get_logger(f"strategy.{name}")
        self.is_enabled = config.get('enabled', True)
        self.min_periods = config.get('min_periods', 20)
        
        # 전략 상태
        self.current_position = None
        self.last_signal = None
        self.signal_history = []
        
        self.logger.info(f"전략 초기화: {self.name}")
    
    @abstractmethod
    def generate_signal(self, data: pd.DataFrame) -> Optional[TradingSignal]:
        """거래 신호 생성 (추상 메서드)"""
        pass
    
    @abstractmethod
    def get_required_columns(self) -> List[str]:
        """필요한 데이터 컬럼 반환 (추상 메서드)"""
        pass
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """데이터 유효성 검사"""
        required_columns = self.get_required_columns()
        
        if data.empty:
            self.logger.warning("데이터가 비어있습니다")
            return False
        
        if len(data) < self.min_periods:
            self.logger.warning(f"데이터 길이가 부족합니다: {len(data)} < {self.min_periods}")
            return False
        
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            self.logger.error(f"필수 컬럼이 누락되었습니다: {missing_columns}")
            return False
        
        return True
    
    def update_position(self, position: Optional[Dict[str, Any]]):
        """현재 포지션 업데이트"""
        self.current_position = position
        if position:
            self.logger.debug(f"포지션 업데이트: {position}")
    
    def add_signal_to_history(self, signal: TradingSignal):
        """신호를 히스토리에 추가"""
        self.signal_history.append(signal)
        self.last_signal = signal
        
        # 히스토리 크기 제한 (최근 100개)
        if len(self.signal_history) > 100:
            self.signal_history = self.signal_history[-100:]
    
    def get_signal_history(self, limit: int = 10) -> List[TradingSignal]:
        """신호 히스토리 조회"""
        return self.signal_history[-limit:]
    
    def get_last_signal(self) -> Optional[TradingSignal]:
        """마지막 신호 조회"""
        return self.last_signal
    
    def is_signal_ready(self, data: pd.DataFrame) -> bool:
        """신호 생성 준비 상태 확인"""
        if not self.is_enabled:
            return False
        
        if not self.validate_data(data):
            return False
        
        return True
    
    def calculate_position_size(self, 
                              account_balance: float, 
                              risk_per_trade: float = 0.01,
                              stop_loss_price: Optional[float] = None,
                              entry_price: float = 0.0) -> float:
        """포지션 크기 계산"""
        if stop_loss_price is None or entry_price == 0:
            # 고정 비율로 계산
            return account_balance * risk_per_trade
        
        # 스탑로스 기반 계산
        risk_amount = account_balance * risk_per_trade
        price_risk = abs(entry_price - stop_loss_price)
        
        if price_risk == 0:
            return 0
        
        position_size = risk_amount / price_risk
        return min(position_size, account_balance * 0.1)  # 최대 10% 제한
    
    def should_exit_position(self, 
                           current_price: float, 
                           entry_price: float,
                           stop_loss_price: Optional[float] = None,
                           take_profit_price: Optional[float] = None) -> Tuple[bool, str]:
        """포지션 청산 여부 확인"""
        if not self.current_position:
            return False, "포지션 없음"
        
        # 스탑로스 확인
        if stop_loss_price:
            if self.current_position['side'] == 'long' and current_price <= stop_loss_price:
                return True, "스탑로스"
            elif self.current_position['side'] == 'short' and current_price >= stop_loss_price:
                return True, "스탑로스"
        
        # 테이크 프로핏 확인
        if take_profit_price:
            if self.current_position['side'] == 'long' and current_price >= take_profit_price:
                return True, "테이크 프로핏"
            elif self.current_position['side'] == 'short' and current_price <= take_profit_price:
                return True, "테이크 프로핏"
        
        return False, "보유 중"
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """전략 정보 반환"""
        return {
            'name': self.name,
            'enabled': self.is_enabled,
            'min_periods': self.min_periods,
            'current_position': self.current_position,
            'last_signal': self.last_signal,
            'signal_count': len(self.signal_history),
            'config': self.config
        }
    
    def reset_strategy(self):
        """전략 상태 초기화"""
        self.current_position = None
        self.last_signal = None
        self.signal_history = []
        self.logger.info(f"전략 상태 초기화: {self.name}")
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', enabled={self.is_enabled})"
