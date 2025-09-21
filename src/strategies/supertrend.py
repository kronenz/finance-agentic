"""
슈퍼트렌드 전략

concept.md에서 제시된 슈퍼트렌드 기반 추세추종 전략을 구현합니다.
"""

import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base_strategy import BaseStrategy, TradingSignal
from ..data.indicators import get_indicators


class SupertrendStrategy(BaseStrategy):
    """슈퍼트렌드 기반 추세추종 전략"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("Supertrend", config)
        
        # 전략 파라미터
        self.atr_period = config.get('atr_period', 10)
        self.atr_multiplier = config.get('atr_multiplier', 3.0)
        self.min_periods = config.get('min_periods', 20)
        
        # 지표 계산기
        self.indicators = get_indicators()
        
        self.logger.info(f"슈퍼트렌드 전략 초기화: ATR={self.atr_period}, Multiplier={self.atr_multiplier}")
    
    def get_required_columns(self) -> List[str]:
        """필요한 데이터 컬럼 반환"""
        return ['high', 'low', 'close']
    
    def generate_signal(self, data: pd.DataFrame) -> Optional[TradingSignal]:
        """슈퍼트렌드 기반 거래 신호 생성"""
        try:
            if not self.is_signal_ready(data):
                return None
            
            # 슈퍼트렌드 지표 계산
            supertrend_data = self.indicators.calculate_supertrend(
                data['high'],
                data['low'],
                data['close'],
                period=self.atr_period,
                multiplier=self.atr_multiplier
            )
            
            supertrend = supertrend_data['supertrend']
            direction = supertrend_data['direction']
            
            # 최신 값들
            current_price = data['close'].iloc[-1]
            current_supertrend = supertrend.iloc[-1]
            current_direction = direction.iloc[-1]
            
            # 이전 값들 (신호 확인용)
            if len(data) < 2:
                return None
            
            prev_direction = direction.iloc[-2]
            prev_price = data['close'].iloc[-2]
            
            signal_type = 'hold'
            strength = 0.0
            metadata = {
                'supertrend_price': current_supertrend,
                'direction': current_direction,
                'atr': supertrend_data['atr'].iloc[-1],
                'price_vs_supertrend': current_price - current_supertrend
            }
            
            # 신호 생성 로직
            if current_direction == 1 and prev_direction == -1:
                # 하락에서 상승으로 전환 (매수 신호)
                signal_type = 'buy'
                strength = min(1.0, abs(current_price - current_supertrend) / current_supertrend * 10)
                self.logger.info(f"매수 신호 생성: 가격={current_price:.2f}, 슈퍼트렌드={current_supertrend:.2f}")
                
            elif current_direction == -1 and prev_direction == 1:
                # 상승에서 하락으로 전환 (매도 신호)
                signal_type = 'sell'
                strength = min(1.0, abs(current_price - current_supertrend) / current_supertrend * 10)
                self.logger.info(f"매도 신호 생성: 가격={current_price:.2f}, 슈퍼트렌드={current_supertrend:.2f}")
            
            # 신호가 있는 경우에만 반환
            if signal_type != 'hold':
                signal = TradingSignal(
                    signal_type=signal_type,
                    strength=strength,
                    price=current_price,
                    timestamp=datetime.now(),
                    metadata=metadata
                )
                
                self.add_signal_to_history(signal)
                return signal
            
            return None
            
        except Exception as e:
            self.logger.error(f"슈퍼트렌드 신호 생성 실패: {e}")
            return None
    
    def get_stop_loss_price(self, entry_price: float, side: str) -> float:
        """스탑로스 가격 계산 (슈퍼트렌드 라인 사용)"""
        try:
            if not hasattr(self, '_last_supertrend_data'):
                return entry_price * 0.95 if side == 'long' else entry_price * 1.05
            
            supertrend = self._last_supertrend_data['supertrend']
            current_supertrend = supertrend.iloc[-1]
            
            # 슈퍼트렌드 라인을 스탑로스로 사용
            return current_supertrend
            
        except Exception as e:
            self.logger.warning(f"스탑로스 가격 계산 실패: {e}")
            return entry_price * 0.95 if side == 'long' else entry_price * 1.05
    
    def get_take_profit_price(self, entry_price: float, side: str, risk_reward_ratio: float = 2.0) -> float:
        """테이크 프로핏 가격 계산"""
        try:
            if not hasattr(self, '_last_supertrend_data'):
                # 기본 리스크:리워드 비율 사용
                if side == 'long':
                    return entry_price * (1 + 0.02 * risk_reward_ratio)
                else:
                    return entry_price * (1 - 0.02 * risk_reward_ratio)
            
            atr = self._last_supertrend_data['atr']
            current_atr = atr.iloc[-1]
            
            # ATR 기반 테이크 프로핏
            if side == 'long':
                return entry_price + (current_atr * risk_reward_ratio)
            else:
                return entry_price - (current_atr * risk_reward_ratio)
                
        except Exception as e:
            self.logger.warning(f"테이크 프로핏 가격 계산 실패: {e}")
            if side == 'long':
                return entry_price * 1.02
            else:
                return entry_price * 0.98
    
    def update_supertrend_data(self, data: pd.DataFrame):
        """슈퍼트렌드 데이터 업데이트 (스탑로스/테이크프로핏 계산용)"""
        try:
            self._last_supertrend_data = self.indicators.calculate_supertrend(
                data['high'],
                data['low'],
                data['close'],
                period=self.atr_period,
                multiplier=self.atr_multiplier
            )
        except Exception as e:
            self.logger.warning(f"슈퍼트렌드 데이터 업데이트 실패: {e}")
    
    def get_strategy_metrics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """전략 성과 지표 계산"""
        try:
            if len(data) < self.min_periods:
                return {}
            
            # 슈퍼트렌드 지표 계산
            supertrend_data = self.indicators.calculate_supertrend(
                data['high'],
                data['low'],
                data['close'],
                period=self.atr_period,
                multiplier=self.atr_multiplier
            )
            
            supertrend = supertrend_data['supertrend']
            direction = supertrend_data['direction']
            atr = supertrend_data['atr']
            
            # 현재 상태
            current_price = data['close'].iloc[-1]
            current_supertrend = supertrend.iloc[-1]
            current_direction = direction.iloc[-1]
            
            # 추세 강도 계산
            price_distance = abs(current_price - current_supertrend)
            trend_strength = price_distance / current_supertrend if current_supertrend > 0 else 0
            
            # ATR 대비 가격 움직임
            current_atr = atr.iloc[-1]
            atr_ratio = price_distance / current_atr if current_atr > 0 else 0
            
            return {
                'current_price': current_price,
                'supertrend_price': current_supertrend,
                'direction': '상승' if current_direction == 1 else '하락',
                'trend_strength': trend_strength,
                'atr_ratio': atr_ratio,
                'atr_value': current_atr,
                'price_vs_supertrend': current_price - current_supertrend,
                'signal_strength': min(1.0, trend_strength * 10)
            }
            
        except Exception as e:
            self.logger.error(f"전략 지표 계산 실패: {e}")
            return {}
    
    def should_exit_position(self, 
                           current_price: float, 
                           entry_price: float,
                           data: pd.DataFrame) -> tuple[bool, str]:
        """포지션 청산 여부 확인 (슈퍼트렌드 기반)"""
        try:
            if not self.current_position:
                return False, "포지션 없음"
            
            # 슈퍼트렌드 데이터 업데이트
            self.update_supertrend_data(data)
            
            # 슈퍼트렌드 방향 확인
            supertrend = self._last_supertrend_data['supertrend']
            direction = self._last_supertrend_data['direction']
            
            current_direction = direction.iloc[-1]
            current_supertrend = supertrend.iloc[-1]
            
            side = self.current_position['side']
            
            # 방향 전환 시 청산
            if side == 'long' and current_direction == -1:
                return True, "슈퍼트렌드 하락 전환"
            elif side == 'short' and current_direction == 1:
                return True, "슈퍼트렌드 상승 전환"
            
            # 슈퍼트렌드 라인 터치 시 청산
            if side == 'long' and current_price <= current_supertrend:
                return True, "슈퍼트렌드 라인 터치"
            elif side == 'short' and current_price >= current_supertrend:
                return True, "슈퍼트렌드 라인 터치"
            
            return False, "보유 중"
            
        except Exception as e:
            self.logger.error(f"청산 조건 확인 실패: {e}")
            return False, "오류"
