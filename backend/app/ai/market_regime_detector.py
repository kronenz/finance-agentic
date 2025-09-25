import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class MarketRegimeType(Enum):
    TREND_UP = "TREND_UP"
    TREND_DOWN = "TREND_DOWN"
    RANGE_HIGH_VOL = "RANGE_HIGH_VOL"
    RANGE_LOW_VOL = "RANGE_LOW_VOL"
    CRASH_EVENT = "CRASH_EVENT"

class MarketRegimeDetector:
    """시장 국면 감지 AI 에이전트"""
    
    def __init__(self, adx_period: int = 14, hurst_period: int = 20):
        self.adx_period = adx_period
        self.hurst_period = hurst_period
        self.confidence_threshold = 0.7
        
    def detect_regime(self, price_data: np.ndarray, volume_data: np.ndarray) -> Dict:
        """
        시장 국면을 감지하고 분석 결과를 반환
        
        Args:
            price_data: 가격 데이터 배열
            volume_data: 거래량 데이터 배열
            
        Returns:
            Dict: 시장 국면 분석 결과
        """
        try:
            # 데이터 검증
            self._validate_data(price_data, volume_data)
            
            # ADX 계산
            adx_value = self._calculate_adx(price_data)
            
            # Hurst 지수 계산
            hurst_exponent = self._calculate_hurst_exponent(price_data)
            
            # 변동성 수준 계산
            volatility_level = self._calculate_volatility_level(price_data)
            
            # 시장 국면 분류
            regime_type, confidence = self._classify_regime(
                adx_value, hurst_exponent, volatility_level, price_data, volume_data
            )
            
            return {
                'regime_type': regime_type,
                'confidence_score': confidence,
                'adx_value': adx_value,
                'hurst_exponent': hurst_exponent,
                'volatility_level': volatility_level,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Market regime detection failed: {e}")
            raise
    
    def _validate_data(self, price_data: np.ndarray, volume_data: np.ndarray) -> None:
        """입력 데이터 검증"""
        if len(price_data) != len(volume_data):
            raise ValueError("Price and volume data must have the same length")
        
        if len(price_data) < self.adx_period:
            raise ValueError(f"Data length must be at least {self.adx_period}")
        
        if np.any(price_data <= 0):
            raise ValueError("Price data must be positive")
        
        if np.any(volume_data < 0):
            raise ValueError("Volume data must be non-negative")
    
    def _calculate_adx(self, price_data: np.ndarray) -> float:
        """ADX (Average Directional Index) 계산"""
        if len(price_data) < self.adx_period + 1:
            return 0.0
        
        # 단순화된 ADX 계산 (실제로는 더 복잡한 계산 필요)
        price_changes = np.diff(price_data)
        positive_changes = np.sum(price_changes[price_changes > 0])
        negative_changes = np.abs(np.sum(price_changes[price_changes < 0]))
        
        if positive_changes + negative_changes == 0:
            return 0.0
        
        adx = (positive_changes - negative_changes) / (positive_changes + negative_changes)
        return min(max(adx * 100, 0), 100)  # 0-100 범위로 정규화
    
    def _calculate_hurst_exponent(self, price_data: np.ndarray) -> float:
        """Hurst 지수 계산 (평균회귀 vs 추세 지속성)"""
        if len(price_data) < self.hurst_period:
            return 0.5
        
        # 단순화된 Hurst 지수 계산
        log_prices = np.log(price_data)
        log_returns = np.diff(log_prices)
        
        # R/S 통계 계산
        mean_return = np.mean(log_returns)
        deviations = log_returns - mean_return
        cumulative_deviations = np.cumsum(deviations)
        
        R = np.max(cumulative_deviations) - np.min(cumulative_deviations)
        S = np.std(log_returns)
        
        if S == 0:
            return 0.5
        
        RS = R / S
        hurst = np.log(RS) / np.log(len(log_returns))
        
        return min(max(hurst, 0), 1)  # 0-1 범위로 제한
    
    def _calculate_volatility_level(self, price_data: np.ndarray) -> str:
        """변동성 수준 계산"""
        if len(price_data) < 2:
            return "LOW"
        
        returns = np.diff(price_data) / price_data[:-1]
        volatility = np.std(returns) * np.sqrt(252)  # 연간 변동성
        
        if volatility < 0.1:
            return "LOW"
        elif volatility < 0.2:
            return "MEDIUM"
        elif volatility < 0.4:
            return "HIGH"
        else:
            return "EXTREME"
    
    def _classify_regime(self, adx: float, hurst: float, volatility: str, 
                        price_data: np.ndarray, volume_data: np.ndarray) -> Tuple[MarketRegimeType, float]:
        """시장 국면 분류"""
        # 가격 추세 분석
        price_trend = self._analyze_price_trend(price_data)
        
        # 거래량 패턴 분석
        volume_pattern = self._analyze_volume_pattern(volume_data)
        
        # 충돌 이벤트 감지
        if self._detect_crash_event(price_data, volume_data):
            return MarketRegimeType.CRASH_EVENT, 0.9
        
        # ADX 기반 추세 강도 분석
        if adx > 25:  # 강한 추세
            if price_trend > 0.02:  # 상승 추세
                confidence = min(adx / 100, 0.95)
                return MarketRegimeType.TREND_UP, confidence
            elif price_trend < -0.02:  # 하락 추세
                confidence = min(adx / 100, 0.95)
                return MarketRegimeType.TREND_DOWN, confidence
        
        # 횡보 구간 분석
        if adx < 20:  # 약한 추세
            if volume_pattern == "HIGH":
                return MarketRegimeType.RANGE_HIGH_VOL, 0.7
            else:
                return MarketRegimeType.RANGE_LOW_VOL, 0.6
        
        # 기본값
        return MarketRegimeType.RANGE_LOW_VOL, 0.5
    
    def _analyze_price_trend(self, price_data: np.ndarray) -> float:
        """가격 추세 분석"""
        if len(price_data) < 2:
            return 0.0
        
        start_price = price_data[0]
        end_price = price_data[-1]
        trend = (end_price - start_price) / start_price
        return trend
    
    def _analyze_volume_pattern(self, volume_data: np.ndarray) -> str:
        """거래량 패턴 분석"""
        if len(volume_data) < 2:
            return "LOW"
        
        avg_volume = np.mean(volume_data)
        recent_volume = np.mean(volume_data[-5:])  # 최근 5개 데이터
        
        if recent_volume > avg_volume * 1.5:
            return "HIGH"
        else:
            return "LOW"
    
    def _detect_crash_event(self, price_data: np.ndarray, volume_data: np.ndarray) -> bool:
        """충돌 이벤트 감지"""
        if len(price_data) < 2:
            return False
        
        # 급격한 가격 하락 감지 (5% 이상)
        price_change = (price_data[-1] - price_data[-2]) / price_data[-2]
        if price_change < -0.05:
            return True
        
        # 거래량 급증 감지
        if len(volume_data) >= 2:
            volume_change = (volume_data[-1] - volume_data[-2]) / volume_data[-2]
            if volume_change > 2.0:  # 200% 이상 증가
                return True
        
        return False
    
    def validate_confidence(self, confidence: float) -> None:
        """신뢰도 점수 검증"""
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("Confidence score must be between 0 and 1")
