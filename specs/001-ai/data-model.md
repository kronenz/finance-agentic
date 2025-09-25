# Data Model: AI 기반 적응형 암호화폐 거래 시스템

## 핵심 엔티티

### MarketRegime
시장의 현재 상태를 나타내는 엔티티
```python
class MarketRegime:
    id: UUID
    timestamp: datetime
    regime_type: str  # "TREND_UP", "TREND_DOWN", "RANGE_HIGH_VOL", "RANGE_LOW_VOL", "CRASH_EVENT"
    confidence_score: float  # 0.0 ~ 1.0
    adx_value: float
    hurst_exponent: float
    volatility_level: str  # "LOW", "MEDIUM", "HIGH", "EXTREME"
    created_at: datetime
    updated_at: datetime
```

**Validation Rules**:
- confidence_score는 0.0과 1.0 사이의 값이어야 함
- regime_type은 사전 정의된 값 중 하나여야 함
- timestamp는 현재 시간보다 과거여야 함

**State Transitions**:
- UNKNOWN → TREND_UP/TREND_DOWN/RANGE_HIGH_VOL/RANGE_LOW_VOL/CRASH_EVENT
- 각 regime_type 간 전환은 confidence_score 변화에 따라 결정

### TradingStrategy
거래 전략을 나타내는 엔티티
```python
class TradingStrategy:
    id: UUID
    name: str
    strategy_type: str  # "TREND_FOLLOWING", "MEAN_REVERSION"
    parameters: dict  # JSON 형태의 전략 파라미터
    is_active: bool
    performance_metrics: dict  # 수익률, 샤프 지수, 최대 낙폭 등
    created_at: datetime
    updated_at: datetime
```

**Validation Rules**:
- strategy_type은 "TREND_FOLLOWING" 또는 "MEAN_REVERSION"이어야 함
- parameters는 유효한 JSON 형태여야 함
- name은 고유해야 함

**State Transitions**:
- INACTIVE → ACTIVE (전략 활성화)
- ACTIVE → INACTIVE (전략 비활성화)
- ACTIVE → EVOLVING (유전 알고리즘에 의한 진화)

### VWAPData
거래량 가중 평균 가격 데이터
```python
class VWAPData:
    id: UUID
    symbol: str  # "BTCUSDT", "ETHUSDT" 등
    timeframe: str  # "1h", "4h", "1d", "1w"
    vwap_value: float
    volume: float
    price: float
    deviation_bands: dict  # 1std, 2std, 3std 밴드 값
    timestamp: datetime
    created_at: datetime
```

**Validation Rules**:
- vwap_value는 양수여야 함
- volume은 0 이상이어야 함
- timeframe은 유효한 값이어야 함 ("1m", "5m", "15m", "1h", "4h", "1d", "1w")

### VolumeProfile
거래량 프로파일 데이터
```python
class VolumeProfile:
    id: UUID
    symbol: str
    timeframe: str
    poc_price: float  # Point of Control
    vah_price: float  # Value Area High
    val_price: float  # Value Area Low
    volume_at_poc: float
    total_volume: float
    lvn_zones: list  # Low Volume Node 구간들
    timestamp: datetime
    created_at: datetime
```

**Validation Rules**:
- poc_price, vah_price, val_price는 양수여야 함
- vah_price >= poc_price >= val_price 관계여야 함
- volume_at_poc <= total_volume이어야 함

### RiskParameters
리스크 관리 파라미터
```python
class RiskParameters:
    id: UUID
    level: str  # "INDIVIDUAL", "PORTFOLIO", "SYSTEM"
    max_position_size: float  # 최대 포지션 크기 (USD)
    max_daily_loss: float  # 일일 최대 손실 (USD)
    max_drawdown: float  # 최대 자본 하락률 (%)
    leverage_limit: float  # 최대 레버리지 배수
    correlation_threshold: float  # 상관관계 임계값
    liquidation_risk_threshold: float  # 연쇄 청산 위험 임계값
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

**Validation Rules**:
- level은 "INDIVIDUAL", "PORTFOLIO", "SYSTEM" 중 하나여야 함
- 모든 수치 값은 0 이상이어야 함
- max_drawdown은 0과 100 사이여야 함

### TradingSignal
AI 에이전트가 생성하는 거래 신호
```python
class TradingSignal:
    id: UUID
    symbol: str
    signal_type: str  # "BUY", "SELL", "HOLD"
    confidence: float  # 0.0 ~ 1.0
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    strategy_id: UUID  # Foreign Key to TradingStrategy
    market_regime_id: UUID  # Foreign Key to MarketRegime
    vwap_data_id: UUID  # Foreign Key to VWAPData
    volume_profile_id: UUID  # Foreign Key to VolumeProfile
    created_at: datetime
    expires_at: datetime
```

**Validation Rules**:
- signal_type은 "BUY", "SELL", "HOLD" 중 하나여야 함
- confidence는 0.0과 1.0 사이여야 함
- entry_price, stop_loss, take_profit은 양수여야 함
- expires_at은 created_at보다 미래여야 함

### MarketData
실시간 시장 데이터
```python
class MarketData:
    id: UUID
    symbol: str
    exchange: str  # "BINANCE", "BYBIT", "OKX" 등
    data_type: str  # "TICK", "OHLCV", "ORDERBOOK", "FUNDING_RATE"
    price: float
    volume: float
    timestamp: datetime
    raw_data: dict  # 원본 데이터 (JSON)
    created_at: datetime
```

**Validation Rules**:
- data_type은 유효한 값이어야 함
- price와 volume은 0 이상이어야 함
- timestamp는 현재 시간과 1분 이내 차이여야 함

### PerformanceMetrics
시스템 성능 지표
```python
class PerformanceMetrics:
    id: UUID
    period: str  # "1H", "1D", "1W", "1M"
    total_return: float  # 총 수익률 (%)
    sharpe_ratio: float  # 샤프 지수
    max_drawdown: float  # 최대 낙폭 (%)
    win_rate: float  # 승률 (%)
    profit_factor: float  # 손익비
    total_trades: int  # 총 거래 횟수
    avg_trade_duration: float  # 평균 거래 지속시간 (분)
    strategy_id: UUID  # Foreign Key to TradingStrategy
    calculated_at: datetime
    created_at: datetime
```

**Validation Rules**:
- period는 유효한 값이어야 함
- win_rate은 0과 100 사이여야 함
- total_trades는 0 이상이어야 함

## 관계 (Relationships)

### 1:N 관계
- TradingStrategy → TradingSignal (하나의 전략이 여러 신호 생성)
- MarketRegime → TradingSignal (하나의 시장 국면이 여러 신호에 영향)
- VWAPData → TradingSignal (하나의 VWAP 데이터가 여러 신호에 사용)
- VolumeProfile → TradingSignal (하나의 거래량 프로파일이 여러 신호에 사용)
- TradingStrategy → PerformanceMetrics (하나의 전략이 여러 성과 지표 생성)

### M:N 관계
- TradingStrategy ↔ MarketRegime (전략과 시장 국면의 다대다 관계)
- MarketData ↔ TradingSignal (시장 데이터와 거래 신호의 다대다 관계)

## 인덱스 전략

### 성능 최적화를 위한 인덱스
```sql
-- 시계열 데이터 조회 최적화
CREATE INDEX idx_market_data_symbol_timestamp ON MarketData(symbol, timestamp);
CREATE INDEX idx_vwap_data_symbol_timestamp ON VWAPData(symbol, timestamp);
CREATE INDEX idx_volume_profile_symbol_timestamp ON VolumeProfile(symbol, timestamp);

-- 거래 신호 조회 최적화
CREATE INDEX idx_trading_signal_symbol_created_at ON TradingSignal(symbol, created_at);
CREATE INDEX idx_trading_signal_strategy_id ON TradingSignal(strategy_id);

-- 성과 지표 조회 최적화
CREATE INDEX idx_performance_metrics_strategy_id ON PerformanceMetrics(strategy_id);
CREATE INDEX idx_performance_metrics_calculated_at ON PerformanceMetrics(calculated_at);
```

## 데이터 보존 정책

### 시계열 데이터
- MarketData: 1년 보존 (실시간 분석용)
- VWAPData: 2년 보존 (장기 패턴 분석용)
- VolumeProfile: 2년 보존 (장기 패턴 분석용)

### 거래 데이터
- TradingSignal: 영구 보존 (성과 분석용)
- PerformanceMetrics: 영구 보존 (성과 분석용)

### 로그 데이터
- 시스템 로그: 6개월 보존
- 에러 로그: 1년 보존
- 감사 로그: 3년 보존

## 데이터 무결성 제약조건

### 외래키 제약조건
- TradingSignal.strategy_id → TradingStrategy.id
- TradingSignal.market_regime_id → MarketRegime.id
- TradingSignal.vwap_data_id → VWAPData.id
- TradingSignal.volume_profile_id → VolumeProfile.id
- PerformanceMetrics.strategy_id → TradingStrategy.id

### 체크 제약조건
- MarketRegime.confidence_score BETWEEN 0.0 AND 1.0
- TradingSignal.confidence BETWEEN 0.0 AND 1.0
- RiskParameters.max_drawdown BETWEEN 0.0 AND 100.0
- PerformanceMetrics.win_rate BETWEEN 0.0 AND 100.0

### 유니크 제약조건
- TradingStrategy.name (전략명은 고유)
- MarketData(symbol, exchange, timestamp) (동일 시점 중복 방지)
