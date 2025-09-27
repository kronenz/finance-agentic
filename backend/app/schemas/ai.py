# AI 관련 Pydantic 스키마
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime

class AgentStatus(BaseModel):
    """에이전트 상태"""
    is_running: bool
    agent_name: str

class AISystemStatus(BaseModel):
    """AI 시스템 상태"""
    timestamp: str
    is_running: bool
    agents: Dict[str, AgentStatus]
    redis_status: str
    message_queues: Dict[str, Dict[str, Any]]

class DataCollectionRequest(BaseModel):
    """데이터 수집 요청"""
    symbols: List[str] = Field(..., description="수집할 심볼 목록")
    exchanges: Optional[List[str]] = Field(None, description="거래소 목록")
    
    class Config:
        schema_extra = {
            "example": {
                "symbols": ["BTC/USDT", "ETH/USDT"],
                "exchanges": ["binance", "coinbase"]
            }
        }

class DataCollectionResponse(BaseModel):
    """데이터 수집 응답"""
    status: str
    message: str
    symbols: List[str]
    exchanges: List[str]
    timestamp: str

class ModelPredictionRequest(BaseModel):
    """모델 예측 요청"""
    symbol: str = Field(..., description="예측할 심볼")
    timeframe: Optional[str] = Field("1h", description="시간 프레임")
    
    class Config:
        schema_extra = {
            "example": {
                "symbol": "BTC/USDT",
                "timeframe": "1h"
            }
        }

class LSTMPrediction(BaseModel):
    """LSTM 예측 결과"""
    predicted_price: float
    confidence: float
    timestamp: str

class XGBoostPrediction(BaseModel):
    """XGBoost 예측 결과"""
    signal: Literal["BUY", "SELL", "HOLD"]
    confidence: float
    probability: Dict[str, float]
    timestamp: str

class ModelPredictions(BaseModel):
    """모델 예측 결과"""
    lstm_prediction: LSTMPrediction
    xgboost_prediction: XGBoostPrediction

class ModelPredictionResponse(BaseModel):
    """모델 예측 응답"""
    symbol: str
    predictions: ModelPredictions
    timestamp: str

class TradingSignalRequest(BaseModel):
    """거래 신호 요청"""
    symbols: List[str] = Field(..., description="신호 생성할 심볼 목록")
    timeframe: Optional[str] = Field("1h", description="시간 프레임")
    
    class Config:
        schema_extra = {
            "example": {
                "symbols": ["BTC/USDT", "ETH/USDT"],
                "timeframe": "1h"
            }
        }

class TradingSignal(BaseModel):
    """거래 신호"""
    symbol: str
    signal: Literal["BUY", "SELL", "HOLD"]
    confidence: float
    price: float
    timestamp: str
    reasoning: str

class TradingSignalResponse(BaseModel):
    """거래 신호 응답"""
    signals: List[TradingSignal]
    timestamp: str

class SystemHealth(BaseModel):
    """시스템 헬스 체크"""
    status: Literal["healthy", "unhealthy"]
    timestamp: str
    components: Dict[str, str]

class MarketDataRequest(BaseModel):
    """시장 데이터 요청"""
    symbol: str
    exchange: str
    timeframe: str = "1h"
    limit: int = Field(100, ge=1, le=1000)
    
    class Config:
        schema_extra = {
            "example": {
                "symbol": "BTC/USDT",
                "exchange": "binance",
                "timeframe": "1h",
                "limit": 100
            }
        }

class MarketDataPoint(BaseModel):
    """시장 데이터 포인트"""
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float

class MarketDataResponse(BaseModel):
    """시장 데이터 응답"""
    symbol: str
    exchange: str
    timeframe: str
    data: List[MarketDataPoint]
    timestamp: str

class TechnicalIndicatorRequest(BaseModel):
    """기술적 지표 요청"""
    symbol: str
    exchange: str
    indicators: List[str] = Field(..., description="계산할 지표 목록")
    
    class Config:
        schema_extra = {
            "example": {
                "symbol": "BTC/USDT",
                "exchange": "binance",
                "indicators": ["rsi", "macd", "bollinger_bands"]
            }
        }

class TechnicalIndicators(BaseModel):
    """기술적 지표"""
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    stoch_k: Optional[float] = None
    stoch_d: Optional[float] = None
    volatility: Optional[float] = None
    trend: Optional[str] = None

class TechnicalIndicatorResponse(BaseModel):
    """기술적 지표 응답"""
    symbol: str
    exchange: str
    indicators: TechnicalIndicators
    timestamp: str

class ModelTrainingRequest(BaseModel):
    """모델 훈련 요청"""
    model_type: Literal["lstm", "xgboost"]
    symbol: str
    start_date: str
    end_date: str
    parameters: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "model_type": "lstm",
                "symbol": "BTC/USDT",
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
                "parameters": {
                    "sequence_length": 60,
                    "epochs": 100
                }
            }
        }

class ModelTrainingResponse(BaseModel):
    """모델 훈련 응답"""
    model_type: str
    symbol: str
    status: str
    training_id: str
    timestamp: str

class ModelEvaluationRequest(BaseModel):
    """모델 평가 요청"""
    model_type: Literal["lstm", "xgboost"]
    symbol: str
    test_data_start: str
    test_data_end: str
    
    class Config:
        schema_extra = {
            "example": {
                "model_type": "lstm",
                "symbol": "BTC/USDT",
                "test_data_start": "2024-01-01",
                "test_data_end": "2024-12-01"
            }
        }

class ModelEvaluationResponse(BaseModel):
    """모델 평가 응답"""
    model_type: str
    symbol: str
    metrics: Dict[str, float]
    timestamp: str

class AnomalyDetectionRequest(BaseModel):
    """이상 징후 감지 요청"""
    symbol: str
    exchange: str
    threshold: float = Field(0.1, ge=0.0, le=1.0)
    
    class Config:
        schema_extra = {
            "example": {
                "symbol": "BTC/USDT",
                "exchange": "binance",
                "threshold": 0.1
            }
        }

class Anomaly(BaseModel):
    """이상 징후"""
    type: str
    severity: Literal["LOW", "MEDIUM", "HIGH"]
    value: float
    timestamp: str

class AnomalyDetectionResponse(BaseModel):
    """이상 징후 감지 응답"""
    symbol: str
    exchange: str
    anomalies: List[Anomaly]
    timestamp: str

class PortfolioRiskRequest(BaseModel):
    """포트폴리오 리스크 요청"""
    assets: Dict[str, float] = Field(..., description="자산 심볼과 비중 맵")

    class Config:
        schema_extra = {
            "example": {
                "assets": {
                    "BTCUSDT": 0.5,
                    "ETHUSDT": 0.3,
                    "SOLUSDT": 0.2
                }
            }
        }

class PortfolioRiskResponse(BaseModel):
    """포트폴리오 리스크 응답"""
    value_at_risk: float = Field(..., description="포트폴리오 VaR (95% 신뢰수준, 1일)")
    sharpe_ratio: float = Field(..., description="포트폴리오 샤프 비율")
    max_drawdown: float = Field(..., description="포트폴리오 최대 낙폭")
    risk_breakdown: Dict[str, float] = Field(..., description="자산별 리스크 기여도")