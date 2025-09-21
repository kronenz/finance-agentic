"""
RSI 평균회귀 전략

concept.md에서 제시된 RSI 기반 평균회귀 전략을 구현합니다.
"""

import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .base_strategy import BaseStrategy, TradingSignal
from ..data.indicators import get_indicators


class RSIMeanReversionStrategy(BaseStrategy):
    """RSI 기반 평균회귀 전략"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("RSI_MeanReversion", config)
        
        # 전략 파라미터
        self.rsi_period = config.get('rsi_period', 14)
        self.oversold_threshold = config.get('oversold_threshold', 30)
        self.overbought_threshold = config.get('overbought_threshold', 70)
        self.hold_days = config.get('hold_days', 10)
        self.min_periods = config.get('min_periods', 20)
        
        # 지표 계산기
        self.indicators = get_indicators()
        
        # 포지션 추적
        self.position_entry_time = None
        self.position_entry_rsi = None
        
        self.logger.info(f"RSI 평균회귀 전략 초기화: RSI={self.rsi_period}, "
                        f"과매도={self.oversold_threshold}, 과매수={self.overbought_threshold}")
    
    def get_required_columns(self) -> List[str]:
        """필요한 데이터 컬럼 반환"""
        return ['close']
    
    def generate_signal(self, data: pd.DataFrame) -> Optional[TradingSignal]:
        """RSI 기반 평균회귀 신호 생성"""
        try:
            if not self.is_signal_ready(data):
                return None
            
            # RSI 계산
            rsi = self.indicators.calculate_rsi(data['close'], self.rsi_period)
            
            # 최신 값들
            current_price = data['close'].iloc[-1]
            current_rsi = rsi.iloc[-1]
            
            # RSI가 유효하지 않은 경우
            if pd.isna(current_rsi):
                return None
            
            signal_type = 'hold'
            strength = 0.0
            metadata = {
                'rsi_value': current_rsi,
                'oversold_threshold': self.oversold_threshold,
                'overbought_threshold': self.overbought_threshold
            }
            
            # 현재 포지션이 있는 경우
            if self.current_position:
                # 포지션 유지 시간 확인
                if self.position_entry_time:
                    days_held = (datetime.now() - self.position_entry_time).days
                    if days_held >= self.hold_days:
                        signal_type = 'sell'  # 강제 청산
                        strength = 1.0
                        metadata['reason'] = '최대 보유 기간 도달'
                        self.logger.info(f"최대 보유 기간 도달로 청산 신호: {days_held}일")
                
                # RSI 중립 구간 복귀 확인
                elif self.oversold_threshold < current_rsi < self.overbought_threshold:
                    signal_type = 'sell'
                    strength = abs(current_rsi - 50) / 50  # 50에서 멀수록 강한 신호
                    metadata['reason'] = 'RSI 중립 구간 복귀'
                    self.logger.info(f"RSI 중립 복귀로 청산 신호: RSI={current_rsi:.2f}")
            
            # 새로운 진입 신호 확인
            else:
                # 과매도 구간에서 매수 신호
                if current_rsi < self.oversold_threshold:
                    signal_type = 'buy'
                    strength = (self.oversold_threshold - current_rsi) / self.oversold_threshold
                    metadata['reason'] = 'RSI 과매도'
                    self.logger.info(f"과매도 매수 신호: RSI={current_rsi:.2f}")
                
                # 과매수 구간에서 매도 신호 (숏 포지션)
                elif current_rsi > self.overbought_threshold:
                    signal_type = 'sell'  # 숏 포지션 진입
                    strength = (current_rsi - self.overbought_threshold) / (100 - self.overbought_threshold)
                    metadata['reason'] = 'RSI 과매수'
                    self.logger.info(f"과매수 매도 신호: RSI={current_rsi:.2f}")
            
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
                
                # 포지션 진입 시 추적 정보 업데이트
                if signal_type == 'buy' and not self.current_position:
                    self.position_entry_time = datetime.now()
                    self.position_entry_rsi = current_rsi
                elif signal_type == 'sell' and self.current_position:
                    self.position_entry_time = None
                    self.position_entry_rsi = None
                
                return signal
            
            return None
            
        except Exception as e:
            self.logger.error(f"RSI 평균회귀 신호 생성 실패: {e}")
            return None
    
    def get_stop_loss_price(self, entry_price: float, side: str) -> float:
        """스탑로스 가격 계산 (ATR 기반)"""
        try:
            # 기본 스탑로스 (2% 손실)
            if side == 'long':
                return entry_price * 0.98
            else:
                return entry_price * 1.02
                
        except Exception as e:
            self.logger.warning(f"스탑로스 가격 계산 실패: {e}")
            return entry_price * 0.98 if side == 'long' else entry_price * 1.02
    
    def get_take_profit_price(self, entry_price: float, side: str) -> float:
        """테이크 프로핏 가격 계산 (RSI 기반)"""
        try:
            # RSI 50 근처를 목표로 설정
            if side == 'long':
                return entry_price * 1.02  # 2% 수익 목표
            else:
                return entry_price * 0.98  # 2% 수익 목표
                
        except Exception as e:
            self.logger.warning(f"테이크 프로핏 가격 계산 실패: {e}")
            if side == 'long':
                return entry_price * 1.02
            else:
                return entry_price * 0.98
    
    def should_exit_position(self, 
                           current_price: float, 
                           entry_price: float,
                           data: pd.DataFrame) -> tuple[bool, str]:
        """포지션 청산 여부 확인 (RSI 기반)"""
        try:
            if not self.current_position:
                return False, "포지션 없음"
            
            # 최대 보유 기간 확인
            if self.position_entry_time:
                days_held = (datetime.now() - self.position_entry_time).days
                if days_held >= self.hold_days:
                    return True, f"최대 보유 기간 도달 ({days_held}일)"
            
            # RSI 계산
            rsi = self.indicators.calculate_rsi(data['close'], self.rsi_period)
            current_rsi = rsi.iloc[-1]
            
            if pd.isna(current_rsi):
                return False, "RSI 계산 불가"
            
            side = self.current_position['side']
            
            # RSI 중립 구간 복귀 확인
            if self.oversold_threshold < current_rsi < self.overbought_threshold:
                return True, f"RSI 중립 구간 복귀 ({current_rsi:.2f})"
            
            # 반대 신호 확인
            if side == 'long' and current_rsi > self.overbought_threshold:
                return True, f"RSI 과매수 ({current_rsi:.2f})"
            elif side == 'short' and current_rsi < self.oversold_threshold:
                return True, f"RSI 과매도 ({current_rsi:.2f})"
            
            return False, "보유 중"
            
        except Exception as e:
            self.logger.error(f"청산 조건 확인 실패: {e}")
            return False, "오류"
    
    def get_strategy_metrics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """전략 성과 지표 계산"""
        try:
            if len(data) < self.min_periods:
                return {}
            
            # RSI 계산
            rsi = self.indicators.calculate_rsi(data['close'], self.rsi_period)
            current_rsi = rsi.iloc[-1]
            
            if pd.isna(current_rsi):
                return {}
            
            # 현재 상태
            current_price = data['close'].iloc[-1]
            
            # RSI 상태 분류
            if current_rsi < self.oversold_threshold:
                rsi_status = "과매도"
                rsi_strength = (self.oversold_threshold - current_rsi) / self.oversold_threshold
            elif current_rsi > self.overbought_threshold:
                rsi_status = "과매수"
                rsi_strength = (current_rsi - self.overbought_threshold) / (100 - self.overbought_threshold)
            else:
                rsi_status = "중립"
                rsi_strength = 0.0
            
            # 포지션 보유 시간
            days_held = 0
            if self.position_entry_time:
                days_held = (datetime.now() - self.position_entry_time).days
            
            return {
                'current_price': current_price,
                'rsi_value': current_rsi,
                'rsi_status': rsi_status,
                'rsi_strength': rsi_strength,
                'oversold_threshold': self.oversold_threshold,
                'overbought_threshold': self.overbought_threshold,
                'days_held': days_held,
                'max_hold_days': self.hold_days,
                'signal_strength': rsi_strength
            }
            
        except Exception as e:
            self.logger.error(f"전략 지표 계산 실패: {e}")
            return {}
    
    def update_position(self, position: Optional[Dict[str, Any]]):
        """포지션 업데이트 (추가 로직)"""
        super().update_position(position)
        
        # 포지션이 청산된 경우 추적 정보 초기화
        if position is None:
            self.position_entry_time = None
            self.position_entry_rsi = None
        elif not self.current_position:  # 새 포지션 진입
            self.position_entry_time = datetime.now()
            # 현재 RSI 값은 다음 신호 생성 시 업데이트됨
    
    def reset_strategy(self):
        """전략 상태 초기화"""
        super().reset_strategy()
        self.position_entry_time = None
        self.position_entry_rsi = None
