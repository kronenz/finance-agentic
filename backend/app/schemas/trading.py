# 거래 관련 Pydantic 스키마
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime

class TradingSignalRequest(BaseModel):
    """거래 신호 요청"""
    symbols: List[str] = Field(..., description="신호 조회할 심볼 목록")
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
    confidence: float = Field(..., ge=0.0, le=1.0, description="신뢰도 (0-1)")
    price: float = Field(..., gt=0, description="현재 가격")
    timestamp: str
    reasoning: str = Field(..., description="신호 생성 이유")

class TradingSignalResponse(BaseModel):
    """거래 신호 응답"""
    signals: List[TradingSignal]
    timestamp: str

class OrderRequest(BaseModel):
    """주문 요청"""
    symbol: str = Field(..., description="거래 심볼")
    side: Literal["BUY", "SELL"] = Field(..., description="매수/매도")
    type: Literal["MARKET", "LIMIT", "STOP", "STOP_LIMIT"] = Field(..., description="주문 유형")
    quantity: float = Field(..., gt=0, description="수량")
    price: Optional[float] = Field(None, gt=0, description="가격 (지정가 주문시 필수)")
    stop_price: Optional[float] = Field(None, gt=0, description="스탑 가격")
    
    class Config:
        schema_extra = {
            "example": {
                "symbol": "BTC/USDT",
                "side": "BUY",
                "type": "LIMIT",
                "quantity": 0.1,
                "price": 50000.0
            }
        }

class OrderStatus(BaseModel):
    """주문 상태"""
    order_id: str
    symbol: str
    side: Literal["BUY", "SELL"]
    type: Literal["MARKET", "LIMIT", "STOP", "STOP_LIMIT"]
    quantity: float
    price: Optional[float]
    stop_price: Optional[float]
    status: Literal["PENDING", "FILLED", "PARTIALLY_FILLED", "CANCELLED", "REJECTED"]
    filled_quantity: Optional[float] = 0.0
    average_price: Optional[float] = None
    created_at: str
    updated_at: str

class OrderResponse(BaseModel):
    """주문 응답"""
    order: OrderStatus
    message: str
    timestamp: str

class Asset(BaseModel):
    """자산"""
    symbol: str
    quantity: float
    current_price: float
    value: float
    pnl: float
    pnl_percentage: float

class PortfolioRequest(BaseModel):
    """포트폴리오 요청"""
    include_pnl: bool = Field(True, description="손익 포함 여부")
    include_history: bool = Field(False, description="히스토리 포함 여부")

class PortfolioResponse(BaseModel):
    """포트폴리오 응답"""
    total_value: float
    total_pnl: float
    total_pnl_percentage: float
    assets: List[Asset]
    timestamp: str

class BacktestRequest(BaseModel):
    """백테스팅 요청"""
    strategy: str = Field(..., description="전략 ID")
    symbol: str = Field(..., description="거래 심볼")
    start_date: str = Field(..., description="시작 날짜 (YYYY-MM-DD)")
    end_date: str = Field(..., description="종료 날짜 (YYYY-MM-DD)")
    initial_capital: float = Field(10000.0, gt=0, description="초기 자본")
    parameters: Optional[Dict[str, Any]] = Field(None, description="전략 파라미터")
    
    class Config:
        schema_extra = {
            "example": {
                "strategy": "rsi_mean_reversion",
                "symbol": "BTC/USDT",
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
                "initial_capital": 10000.0,
                "parameters": {
                    "rsi_period": 14,
                    "oversold_threshold": 30
                }
            }
        }

class BacktestResponse(BaseModel):
    """백테스팅 응답"""
    backtest_id: str
    strategy: str
    symbol: str
    start_date: str
    end_date: str
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    profitable_trades: int
    losing_trades: int
    average_win: float
    average_loss: float
    profit_factor: float
    timestamp: str

class StrategyRequest(BaseModel):
    """전략 생성 요청"""
    name: str = Field(..., description="전략 이름")
    description: str = Field(..., description="전략 설명")
    parameters: Dict[str, Any] = Field(..., description="전략 파라미터")
    is_active: bool = Field(True, description="활성화 여부")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Custom RSI Strategy",
                "description": "사용자 정의 RSI 전략",
                "parameters": {
                    "rsi_period": 14,
                    "oversold_threshold": 25,
                    "overbought_threshold": 75
                },
                "is_active": True
            }
        }

class StrategyResponse(BaseModel):
    """전략 응답"""
    strategy_id: str
    name: str
    description: str
    parameters: Dict[str, Any]
    performance: Dict[str, float]
    is_active: bool
    created_at: str

class TradeHistoryRequest(BaseModel):
    """거래 히스토리 요청"""
    symbol: Optional[str] = Field(None, description="거래 심볼")
    start_date: Optional[str] = Field(None, description="시작 날짜")
    end_date: Optional[str] = Field(None, description="종료 날짜")
    limit: int = Field(100, ge=1, le=1000, description="조회 개수")
    offset: int = Field(0, ge=0, description="오프셋")

class TradeHistory(BaseModel):
    """거래 히스토리"""
    trade_id: str
    symbol: str
    side: Literal["BUY", "SELL"]
    quantity: float
    price: float
    value: float
    fee: float
    pnl: Optional[float] = None
    timestamp: str

class TradeHistoryResponse(BaseModel):
    """거래 히스토리 응답"""
    trades: List[TradeHistory]
    total_count: int
    timestamp: str

class PerformanceMetrics(BaseModel):
    """성과 지표"""
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    calmar_ratio: float
    win_rate: float
    profit_factor: float
    average_win: float
    average_loss: float
    total_trades: int
    profitable_trades: int
    losing_trades: int

class PerformanceRequest(BaseModel):
    """성과 조회 요청"""
    start_date: str = Field(..., description="시작 날짜")
    end_date: str = Field(..., description="종료 날짜")
    symbol: Optional[str] = Field(None, description="거래 심볼")
    strategy: Optional[str] = Field(None, description="전략 ID")

class PerformanceResponse(BaseModel):
    """성과 응답"""
    metrics: PerformanceMetrics
    period: str
    timestamp: str
