from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BaseStrategy(ABC):
    """거래 전략의 기본 클래스"""
    
    def __init__(self, name: str, parameters: Dict[str, Any]):
        self.name = name
        self.parameters = parameters
        self.is_active = False
        self.performance_metrics = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
    @abstractmethod
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        시장 데이터를 분석하여 거래 신호를 생성
        
        Args:
            market_data: 시장 데이터
            
        Returns:
            Dict: 분석 결과 및 거래 신호
        """
        pass
    
    @abstractmethod
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        전략 파라미터 검증
        
        Args:
            parameters: 검증할 파라미터
            
        Returns:
            bool: 유효성 여부
        """
        pass
    
    def activate(self) -> None:
        """전략 활성화"""
        if self.validate_parameters(self.parameters):
            self.is_active = True
            self.updated_at = datetime.now()
            logger.info(f"Strategy {self.name} activated")
        else:
            raise ValueError(f"Invalid parameters for strategy {self.name}")
    
    def deactivate(self) -> None:
        """전략 비활성화"""
        self.is_active = False
        self.updated_at = datetime.now()
        logger.info(f"Strategy {self.name} deactivated")
    
    def update_performance(self, metrics: Dict[str, Any]) -> None:
        """성과 지표 업데이트"""
        self.performance_metrics.update(metrics)
        self.updated_at = datetime.now()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """성과 요약 반환"""
        return {
            'strategy_name': self.name,
            'is_active': self.is_active,
            'performance_metrics': self.performance_metrics,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
