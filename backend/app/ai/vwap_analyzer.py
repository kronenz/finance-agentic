import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class VWAPAnalyzer:
    """VWAP (Volume Weighted Average Price) 분석 AI 에이전트"""
    
    def __init__(self, std_dev_multiplier: float = 2.0):
        self.std_dev_multiplier = std_dev_multiplier
        
    def calculate_vwap(self, prices: np.ndarray, volumes: np.ndarray) -> float:
        """
        VWAP 계산
        
        Args:
            prices: 가격 배열
            volumes: 거래량 배열
            
        Returns:
            float: VWAP 값
        """
        try:
            self._validate_data(prices, volumes)
            
            # VWAP = Σ(Price × Volume) / Σ(Volume)
            vwap = np.sum(prices * volumes) / np.sum(volumes)
            
            return float(vwap)
            
        except Exception as e:
            logger.error(f"VWAP calculation failed: {e}")
            raise
    
    def calculate_deviation_bands(self, vwap: float, prices: np.ndarray, 
                                volumes: np.ndarray) -> Dict[str, float]:
        """
        표준편차 밴드 계산
        
        Args:
            vwap: VWAP 값
            prices: 가격 배열
            volumes: 거래량 배열
            
        Returns:
            Dict: 표준편차 밴드 값들
        """
        try:
            # 가격의 표준편차 계산
            std_dev = np.std(prices)
            
            # 표준편차 밴드 계산
            bands = {
                'upper_1std': vwap + std_dev,
                'upper_2std': vwap + 2 * std_dev,
                'upper_3std': vwap + 3 * std_dev,
                'lower_1std': vwap - std_dev,
                'lower_2std': vwap - 2 * std_dev,
                'lower_3std': vwap - 3 * std_dev
            }
            
            return bands
            
        except Exception as e:
            logger.error(f"Deviation bands calculation failed: {e}")
            raise
    
    def generate_signal(self, current_price: float, vwap: float, 
                       upper_band: float, lower_band: float) -> str:
        """
        VWAP 기반 거래 신호 생성
        
        Args:
            current_price: 현재 가격
            vwap: VWAP 값
            upper_band: 상단 밴드
            lower_band: 하단 밴드
            
        Returns:
            str: 거래 신호 ('BUY', 'SELL', 'HOLD')
        """
        try:
            # VWAP 대비 현재 가격 위치 분석
            if current_price > upper_band:
                return 'SELL'  # 상단 밴드 위 - 매도 신호
            elif current_price < lower_band:
                return 'BUY'   # 하단 밴드 아래 - 매수 신호
            else:
                return 'HOLD'  # 밴드 내부 - 보유
                
        except Exception as e:
            logger.error(f"Signal generation failed: {e}")
            raise
    
    def analyze_multiple_timeframes(self, data: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        다중 시간대 VWAP 분석
        
        Args:
            data: 시간대별 데이터 {'1h': {'prices': [...], 'volumes': [...]}, ...}
            
        Returns:
            Dict: 시간대별 VWAP 분석 결과
        """
        try:
            results = {}
            
            for timeframe, tf_data in data.items():
                prices = np.array(tf_data['prices'])
                volumes = np.array(tf_data['volumes'])
                
                # VWAP 계산
                vwap = self.calculate_vwap(prices, volumes)
                
                # 표준편차 밴드 계산
                bands = self.calculate_deviation_bands(vwap, prices, volumes)
                
                # 현재 가격 (마지막 가격)
                current_price = prices[-1]
                
                # 신호 생성
                signal = self.generate_signal(
                    current_price, vwap, 
                    bands['upper_1std'], bands['lower_1std']
                )
                
                results[timeframe] = {
                    'vwap': vwap,
                    'current_price': current_price,
                    'signal': signal,
                    'deviation_bands': bands,
                    'timestamp': datetime.now()
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Multi-timeframe analysis failed: {e}")
            raise
    
    def calculate_vwap_confidence(self, prices: np.ndarray, volumes: np.ndarray) -> float:
        """
        VWAP 신뢰도 계산 (거래량 기반)
        
        Args:
            prices: 가격 배열
            volumes: 거래량 배열
            
        Returns:
            float: 신뢰도 점수 (0-1)
        """
        try:
            if len(prices) < 2:
                return 0.0
            
            # 거래량 일관성 분석
            volume_consistency = 1.0 - (np.std(volumes) / np.mean(volumes))
            
            # 가격 안정성 분석
            price_stability = 1.0 - (np.std(prices) / np.mean(prices))
            
            # 데이터 포인트 수 고려
            data_points_factor = min(len(prices) / 100, 1.0)
            
            # 종합 신뢰도 계산
            confidence = (volume_consistency * 0.4 + 
                         price_stability * 0.4 + 
                         data_points_factor * 0.2)
            
            return min(max(confidence, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"VWAP confidence calculation failed: {e}")
            return 0.0
    
    def detect_vwap_divergence(self, prices: np.ndarray, volumes: np.ndarray, 
                              vwap_values: np.ndarray) -> Dict[str, bool]:
        """
        VWAP 다이버전스 감지
        
        Args:
            prices: 가격 배열
            volumes: 거래량 배열
            vwap_values: VWAP 값 배열
            
        Returns:
            Dict: 다이버전스 감지 결과
        """
        try:
            if len(prices) < 10 or len(vwap_values) < 10:
                return {'bullish_divergence': False, 'bearish_divergence': False}
            
            # 최근 10개 데이터 포인트 분석
            recent_prices = prices[-10:]
            recent_vwap = vwap_values[-10:]
            
            # 가격과 VWAP의 상관관계 분석
            price_trend = np.polyfit(range(len(recent_prices)), recent_prices, 1)[0]
            vwap_trend = np.polyfit(range(len(recent_vwap)), recent_vwap, 1)[0]
            
            # 다이버전스 감지
            bullish_divergence = (price_trend < 0 and vwap_trend > 0)  # 가격 하락, VWAP 상승
            bearish_divergence = (price_trend > 0 and vwap_trend < 0)  # 가격 상승, VWAP 하락
            
            return {
                'bullish_divergence': bullish_divergence,
                'bearish_divergence': bearish_divergence
            }
            
        except Exception as e:
            logger.error(f"VWAP divergence detection failed: {e}")
            return {'bullish_divergence': False, 'bearish_divergence': False}
    
    def _validate_data(self, prices: np.ndarray, volumes: np.ndarray) -> None:
        """입력 데이터 검증"""
        if len(prices) != len(volumes):
            raise ValueError("Prices and volumes must have the same length")
        
        if len(prices) == 0:
            raise ValueError("Data cannot be empty")
        
        if np.any(prices <= 0):
            raise ValueError("Prices must be positive")
        
        if np.any(volumes < 0):
            raise ValueError("Volumes must be non-negative")
        
        if np.sum(volumes) == 0:
            raise ValueError("Total volume cannot be zero")
