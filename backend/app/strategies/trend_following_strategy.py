import numpy as np
from typing import Dict, Any
from datetime import datetime
import logging
from .base_strategy import BaseStrategy

logger = logging.getLogger(__name__)

class TrendFollowingStrategy(BaseStrategy):
    """추세 추종 전략"""
    
    def __init__(self, parameters: Dict[str, Any]):
        super().__init__("TrendFollowing", parameters)
        self.strategy_type = "TREND_FOLLOWING"
        
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        추세 추종 분석 수행
        
        Args:
            market_data: 시장 데이터 {'prices': [...], 'volumes': [...], 'regime': {...}}
            
        Returns:
            Dict: 분석 결과
        """
        try:
            prices = np.array(market_data['prices'])
            volumes = np.array(market_data['volumes'])
            
            # 이동평균 계산
            short_ma = self._calculate_moving_average(prices, self.parameters['short_period'])
            long_ma = self._calculate_moving_average(prices, self.parameters['long_period'])
            
            # MACD 계산
            macd_line, signal_line, histogram = self._calculate_macd(prices)
            
            # RSI 계산
            rsi = self._calculate_rsi(prices, self.parameters['rsi_period'])
            
            # 추세 강도 분석
            trend_strength = self._analyze_trend_strength(prices, short_ma, long_ma)
            
            # 거래 신호 생성
            signal = self._generate_signal(
                prices, short_ma, long_ma, macd_line, signal_line, rsi, trend_strength
            )
            
            # 신뢰도 계산
            confidence = self._calculate_confidence(
                trend_strength, rsi, macd_line, signal_line
            )
            
            return {
                'signal': signal,
                'confidence': confidence,
                'trend_strength': trend_strength,
                'short_ma': short_ma,
                'long_ma': long_ma,
                'macd': {'line': macd_line, 'signal': signal_line, 'histogram': histogram},
                'rsi': rsi,
                'reasoning': self._generate_reasoning(signal, trend_strength, rsi),
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Trend following analysis failed: {e}")
            return {
                'signal': 'HOLD',
                'confidence': 0.0,
                'error': str(e),
                'timestamp': datetime.now()
            }
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """파라미터 검증"""
        required_params = ['short_period', 'long_period', 'rsi_period', 'macd_fast', 'macd_slow', 'macd_signal']
        
        if not all(param in parameters for param in required_params):
            return False
        
        # 기간 검증
        if parameters['short_period'] >= parameters['long_period']:
            return False
        
        if parameters['rsi_period'] <= 0:
            return False
        
        # MACD 파라미터 검증
        if parameters['macd_fast'] >= parameters['macd_slow']:
            return False
        
        return True
    
    def _calculate_moving_average(self, prices: np.ndarray, period: int) -> float:
        """이동평균 계산"""
        if len(prices) < period:
            return prices[-1] if len(prices) > 0 else 0.0
        return np.mean(prices[-period:])
    
    def _calculate_macd(self, prices: np.ndarray) -> tuple:
        """MACD 계산"""
        fast_period = self.parameters['macd_fast']
        slow_period = self.parameters['macd_slow']
        signal_period = self.parameters['macd_signal']
        
        if len(prices) < slow_period:
            return 0.0, 0.0, 0.0
        
        # 지수이동평균 계산
        ema_fast = self._calculate_ema(prices, fast_period)
        ema_slow = self._calculate_ema(prices, slow_period)
        
        macd_line = ema_fast - ema_slow
        
        # MACD 신호선 계산 (MACD의 이동평균)
        if len(prices) >= slow_period + signal_period:
            macd_values = []
            for i in range(slow_period, len(prices)):
                ema_f = self._calculate_ema(prices[:i+1], fast_period)
                ema_s = self._calculate_ema(prices[:i+1], slow_period)
                macd_values.append(ema_f - ema_s)
            
            signal_line = np.mean(macd_values[-signal_period:]) if len(macd_values) >= signal_period else macd_line
        else:
            signal_line = macd_line
        
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def _calculate_ema(self, prices: np.ndarray, period: int) -> float:
        """지수이동평균 계산"""
        if len(prices) < period:
            return prices[-1] if len(prices) > 0 else 0.0
        
        alpha = 2.0 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = alpha * price + (1 - alpha) * ema
        
        return ema
    
    def _calculate_rsi(self, prices: np.ndarray, period: int) -> float:
        """RSI 계산"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _analyze_trend_strength(self, prices: np.ndarray, short_ma: float, long_ma: float) -> float:
        """추세 강도 분석"""
        if long_ma == 0:
            return 0.0
        
        # 이동평균 간의 거리
        ma_distance = abs(short_ma - long_ma) / long_ma
        
        # 가격의 추세 일관성
        if len(prices) < 5:
            return 0.0
        
        recent_prices = prices[-5:]
        price_trend = np.polyfit(range(len(recent_prices)), recent_prices, 1)[0]
        trend_consistency = abs(price_trend) / np.mean(recent_prices)
        
        # 종합 추세 강도
        trend_strength = (ma_distance * 0.6 + trend_consistency * 0.4)
        
        return min(trend_strength, 1.0)
    
    def _generate_signal(self, prices: np.ndarray, short_ma: float, long_ma: float, 
                        macd_line: float, signal_line: float, rsi: float, trend_strength: float) -> str:
        """거래 신호 생성"""
        # 기본 추세 신호
        if short_ma > long_ma and macd_line > signal_line:
            base_signal = 'BUY'
        elif short_ma < long_ma and macd_line < signal_line:
            base_signal = 'SELL'
        else:
            base_signal = 'HOLD'
        
        # RSI 필터링
        if rsi > 70:  # 과매수
            if base_signal == 'BUY':
                return 'HOLD'
        elif rsi < 30:  # 과매도
            if base_signal == 'SELL':
                return 'HOLD'
        
        # 추세 강도 필터링
        if trend_strength < 0.1:  # 약한 추세
            return 'HOLD'
        
        return base_signal
    
    def _calculate_confidence(self, trend_strength: float, rsi: float, 
                            macd_line: float, signal_line: float) -> float:
        """신뢰도 계산"""
        # 추세 강도 기반 신뢰도
        trend_confidence = trend_strength
        
        # RSI 기반 신뢰도 (극단값에서 높은 신뢰도)
        rsi_confidence = 1.0 - abs(rsi - 50) / 50
        
        # MACD 기반 신뢰도
        macd_distance = abs(macd_line - signal_line)
        macd_confidence = min(macd_distance / 10, 1.0)  # 정규화
        
        # 종합 신뢰도
        confidence = (trend_confidence * 0.5 + rsi_confidence * 0.3 + macd_confidence * 0.2)
        
        return min(max(confidence, 0.0), 1.0)
    
    def _generate_reasoning(self, signal: str, trend_strength: float, rsi: float) -> str:
        """신호 근거 생성"""
        reasoning_parts = []
        
        if signal == 'BUY':
            reasoning_parts.append("상승 추세 감지")
        elif signal == 'SELL':
            reasoning_parts.append("하락 추세 감지")
        else:
            reasoning_parts.append("추세 불분명")
        
        reasoning_parts.append(f"추세 강도: {trend_strength:.2f}")
        reasoning_parts.append(f"RSI: {rsi:.1f}")
        
        return " | ".join(reasoning_parts)
