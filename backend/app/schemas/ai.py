# AI/ML 관련 Pydantic 스키마
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class MarketRegime(str, Enum):
    """시장 국면 열거형"""
    TRENDING = "trending"
    MEAN_REVERSION = "mean_reversion"
    UNKNOWN = "unknown"

class RiskLevel(str, Enum):
    """리스크 레벨 열거형"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class StrategyType(str, Enum):
    """전략 타입 열거형"""
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    SCALPING = "scalping"

# 시장 분석 관련 스키마

class MarketAnalysisRequest(BaseModel):
    """시장 분석 요청"""
    symbol: str = Field(..., description="거래 심볼 (예: BTCUSDT)")
    price_data: List[Dict[str, Any]] = Field(..., description="가격 데이터")
    update_model: bool = Field(False, description="모델 업데이트 여부")
    regime_label: Optional[str] = Field(None, description="시장 국면 라벨 (훈련용)")
    
    @validator('price_data')
    def validate_price_data(cls, v):
        if not v:
            raise ValueError('price_data cannot be empty')
        
        # 필수 컬럼 확인
        required_columns = ['open', 'high', 'low', 'close']
        for i, data in enumerate(v):
            for col in required_columns:
                if col not in data:
                    raise ValueError(f'Missing required column {col} in price_data[{i}]')
        
        return v

class MarketAnalysisResponse(BaseModel):
    """시장 분석 응답"""
    symbol: str
    regime: MarketRegime
    confidence: float = Field(..., ge=0.0, le=1.0, description="예측 신뢰도")
    probabilities: Dict[str, float] = Field(..., description="각 국면별 확률")
    market_indicators: Dict[str, float] = Field(..., description="시장 지표")
    timestamp: str

# 전략 추천 관련 스키마

class StrategyRecommendationRequest(BaseModel):
    """전략 추천 요청"""
    profile_updates: Optional[Dict[str, Any]] = Field(None, description="프로필 업데이트")
    market_conditions: Optional[Dict[str, Any]] = Field(None, description="시장 조건")
    risk_preference: Optional[RiskLevel] = Field(None, description="리스크 선호도")

class StrategyRecommendationResponse(BaseModel):
    """전략 추천 응답"""
    strategy_id: str
    strategy_name: str
    score: float = Field(..., ge=0.0, le=1.0, description="추천 점수")
    confidence: float = Field(..., ge=0.0, le=1.0, description="신뢰도")
    description: str
    risk_level: RiskLevel
    strategy_type: Optional[StrategyType] = None
    expected_return: Optional[float] = None
    max_drawdown: Optional[float] = None

# 리스크 평가 관련 스키마

class RiskAssessmentRequest(BaseModel):
    """리스크 평가 요청"""
    market_data: Dict[str, Any] = Field(..., description="시장 데이터")
    portfolio_data: Optional[Dict[str, Any]] = Field(None, description="포트폴리오 데이터")
    assessment_type: str = Field("comprehensive", description="평가 타입")

class RiskAssessmentResponse(BaseModel):
    """리스크 평가 응답"""
    total_risk_score: float = Field(..., ge=0.0, le=1.0, description="전체 리스크 점수")
    risk_level: RiskLevel
    market_risk: float = Field(..., ge=0.0, le=1.0, description="시장 리스크")
    portfolio_risk: float = Field(..., ge=0.0, le=1.0, description="포트폴리오 리스크")
    recommendations: List[str] = Field(..., description="권장사항")
    timestamp: str
    risk_breakdown: Optional[Dict[str, float]] = None
    stress_test_results: Optional[Dict[str, Any]] = None

# 사용자 프로필 관련 스키마

class UserProfileUpdate(BaseModel):
    """사용자 프로필 업데이트"""
    risk_tolerance: Optional[float] = Field(None, ge=0.0, le=1.0, description="리스크 허용도")
    trading_experience: Optional[float] = Field(None, ge=0.0, le=1.0, description="거래 경험")
    investment_horizon: Optional[float] = Field(None, ge=0.0, le=1.0, description="투자 기간")
    portfolio_size: Optional[float] = Field(None, ge=0.0, description="포트폴리오 크기")
    preferences: Optional[Dict[str, Any]] = Field(None, description="선호도")
    
    @validator('risk_tolerance')
    def validate_risk_tolerance(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError('risk_tolerance must be between 0 and 1')
        return v
    
    @validator('trading_experience')
    def validate_trading_experience(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError('trading_experience must be between 0 and 1')
        return v
    
    @validator('investment_horizon')
    def validate_investment_horizon(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError('investment_horizon must be between 0 and 1')
        return v

class UserProfileResponse(BaseModel):
    """사용자 프로필 응답"""
    user_id: str
    risk_tolerance: float
    trading_experience: float
    investment_horizon: float
    portfolio_size: float
    preferences: Dict[str, Any]
    trading_history: List[Dict[str, Any]]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

# 모델 훈련 관련 스키마

class ModelTrainingRequest(BaseModel):
    """모델 훈련 요청"""
    model_type: str = Field(..., description="모델 타입")
    training_data: List[Dict[str, Any]] = Field(..., description="훈련 데이터")
    hyperparameters: Optional[Dict[str, Any]] = Field(None, description="하이퍼파라미터")
    validation_split: float = Field(0.2, ge=0.0, le=0.5, description="검증 데이터 비율")

class ModelTrainingResponse(BaseModel):
    """모델 훈련 응답"""
    model_type: str
    training_status: str
    accuracy: Optional[float] = None
    loss: Optional[float] = None
    training_samples: int
    validation_samples: int
    training_time: float
    model_id: str

# A/B 테스트 관련 스키마

class ABTestRequest(BaseModel):
    """A/B 테스트 요청"""
    test_name: str = Field(..., description="테스트 이름")
    strategy_a: str = Field(..., description="전략 A")
    strategy_b: str = Field(..., description="전략 B")
    traffic_split: float = Field(0.5, ge=0.0, le=1.0, description="트래픽 분할 비율")
    duration_days: int = Field(7, ge=1, le=30, description="테스트 기간 (일)")

class ABTestResponse(BaseModel):
    """A/B 테스트 응답"""
    test_id: str
    test_name: str
    status: str
    strategy_a: str
    strategy_b: str
    traffic_split: float
    start_date: str
    end_date: str
    results: Optional[Dict[str, Any]] = None

# 모니터링 관련 스키마

class ModelPerformanceMetrics(BaseModel):
    """모델 성능 메트릭"""
    model_type: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: float
    training_samples: int
    validation_samples: int
    last_updated: str

class SystemHealthMetrics(BaseModel):
    """시스템 상태 메트릭"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    gpu_usage: Optional[float] = None
    active_models: int
    total_predictions: int
    average_latency: float
    error_rate: float
    timestamp: str

# 알림 관련 스키마

class AIAlertRequest(BaseModel):
    """AI 알림 요청"""
    alert_type: str = Field(..., description="알림 타입")
    message: str = Field(..., description="알림 메시지")
    priority: str = Field("medium", description="우선순위")
    user_id: Optional[str] = Field(None, description="사용자 ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="메타데이터")

class AIAlertResponse(BaseModel):
    """AI 알림 응답"""
    alert_id: str
    alert_type: str
    message: str
    priority: str
    status: str
    created_at: str
    user_id: Optional[str] = None

# 배치 처리 관련 스키마

class BatchPredictionRequest(BaseModel):
    """배치 예측 요청"""
    prediction_type: str = Field(..., description="예측 타입")
    data: List[Dict[str, Any]] = Field(..., description="예측 데이터")
    model_version: Optional[str] = Field(None, description="모델 버전")
    output_format: str = Field("json", description="출력 형식")

class BatchPredictionResponse(BaseModel):
    """배치 예측 응답"""
    job_id: str
    prediction_type: str
    status: str
    total_samples: int
    processed_samples: int
    results: Optional[List[Dict[str, Any]]] = None
    created_at: str
    completed_at: Optional[str] = None
