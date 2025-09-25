# API 문서: AI 기반 암호화폐 거래 시스템

**버전**: 1.0.0  
**날짜**: 2024-12-19  
**기본 URL**: `http://localhost:8000`

## 개요

AI 기반 암호화폐 거래 시스템의 RESTful API 문서입니다. 이 API는 실시간 시장 분석, AI 에이전트 모니터링, 거래 신호 생성, 리스크 관리 등의 기능을 제공합니다.

## 인증

모든 API 요청은 JWT 토큰을 사용한 인증이 필요합니다.

```http
Authorization: Bearer <your-jwt-token>
```

## 기본 응답 형식

### 성공 응답
```json
{
  "success": true,
  "data": { ... },
  "message": "요청이 성공적으로 처리되었습니다.",
  "timestamp": "2024-12-19T10:30:00Z"
}
```

### 에러 응답
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "요청 데이터가 유효하지 않습니다.",
    "details": { ... }
  },
  "timestamp": "2024-12-19T10:30:00Z"
}
```

## 엔드포인트

### 1. 시스템 상태

#### GET /health
시스템 상태를 확인합니다.

**응답:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "uptime": 3600,
    "services": {
      "database": "connected",
      "redis": "connected",
      "ai_agents": "active"
    }
  }
}
```

### 2. 시장 분석

#### GET /v1/trading/market-regime
현재 시장 국면을 조회합니다.

**쿼리 파라미터:**
- `symbol` (선택): 거래 심볼 (기본값: BTCUSDT)
- `timeframe` (선택): 시간대 (기본값: 1h)

**응답:**
```json
{
  "success": true,
  "data": {
    "regime_type": "TREND_UP",
    "confidence_score": 0.85,
    "adx_value": 25.5,
    "hurst_exponent": 0.6,
    "volatility_level": "MEDIUM",
    "timestamp": "2024-12-19T10:30:00Z"
  }
}
```

#### GET /v1/trading/vwap/{symbol}
VWAP 데이터를 조회합니다.

**경로 파라미터:**
- `symbol`: 거래 심볼 (예: BTCUSDT)

**쿼리 파라미터:**
- `timeframe`: 시간대 (1m, 5m, 15m, 1h, 4h, 1d)
- `limit`: 반환할 데이터 수 (기본값: 100)

**응답:**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": "2024-12-19T10:00:00Z",
      "vwap_value": 45000.0,
      "volume": 1000.0,
      "price": 45100.0,
      "deviation_bands": {
        "upper_1std": 45500.0,
        "lower_1std": 44500.0,
        "upper_2std": 46000.0,
        "lower_2std": 44000.0
      }
    }
  ]
}
```

#### GET /v1/trading/volume-profile/{symbol}
거래량 프로파일 데이터를 조회합니다.

**경로 파라미터:**
- `symbol`: 거래 심볼

**쿼리 파라미터:**
- `timeframe`: 시간대

**응답:**
```json
{
  "success": true,
  "data": {
    "poc_price": 45000.0,
    "vah_price": 45200.0,
    "val_price": 44800.0,
    "volume_at_poc": 5000.0,
    "total_volume": 10000.0,
    "lvn_zones": [
      {
        "low": 44900.0,
        "high": 44950.0,
        "volume": 100.0
      }
    ],
    "timestamp": "2024-12-19T10:30:00Z"
  }
}
```

### 3. 거래 신호

#### GET /v1/trading/signals
거래 신호 목록을 조회합니다.

**쿼리 파라미터:**
- `symbol` (선택): 거래 심볼
- `signal_type` (선택): 신호 타입 (BUY, SELL, HOLD)
- `limit` (선택): 반환할 데이터 수 (기본값: 50)
- `offset` (선택): 오프셋 (기본값: 0)

**응답:**
```json
{
  "success": true,
  "data": [
    {
      "id": "signal_123",
      "symbol": "BTCUSDT",
      "signal_type": "BUY",
      "confidence": 0.85,
      "entry_price": 45000.0,
      "stop_loss": 43000.0,
      "take_profit": 48000.0,
      "position_size": 1000.0,
      "strategy_id": "strategy_456",
      "created_at": "2024-12-19T10:30:00Z",
      "expires_at": "2024-12-19T11:30:00Z"
    }
  ],
  "pagination": {
    "total": 100,
    "limit": 50,
    "offset": 0,
    "has_next": true
  }
}
```

#### POST /v1/trading/signals
새로운 거래 신호를 생성합니다.

**요청 본문:**
```json
{
  "symbol": "BTCUSDT",
  "signal_type": "BUY",
  "confidence": 0.85,
  "entry_price": 45000.0,
  "stop_loss": 43000.0,
  "take_profit": 48000.0,
  "position_size": 1000.0,
  "strategy_id": "strategy_456"
}
```

**응답:**
```json
{
  "success": true,
  "data": {
    "id": "signal_123",
    "status": "created",
    "created_at": "2024-12-19T10:30:00Z"
  }
}
```

### 4. 포지션 관리

#### GET /v1/trading/positions
현재 포지션 목록을 조회합니다.

**쿼리 파라미터:**
- `symbol` (선택): 거래 심볼
- `status` (선택): 포지션 상태 (OPEN, CLOSED)

**응답:**
```json
{
  "success": true,
  "data": [
    {
      "id": "pos_123",
      "symbol": "BTCUSDT",
      "side": "BUY",
      "size": 0.1,
      "entry_price": 45000.0,
      "current_price": 46000.0,
      "unrealized_pnl": 100.0,
      "unrealized_pnl_percentage": 0.22,
      "leverage": 2.0,
      "created_at": "2024-12-19T10:00:00Z"
    }
  ]
}
```

#### POST /v1/trading/positions
새로운 포지션을 생성합니다.

**요청 본문:**
```json
{
  "symbol": "BTCUSDT",
  "side": "BUY",
  "size": 0.1,
  "entry_price": 45000.0,
  "leverage": 2.0,
  "stop_loss": 43000.0,
  "take_profit": 48000.0
}
```

#### DELETE /v1/trading/positions/{position_id}
포지션을 종료합니다.

**경로 파라미터:**
- `position_id`: 포지션 ID

**응답:**
```json
{
  "success": true,
  "data": {
    "id": "pos_123",
    "status": "closed",
    "exit_price": 47000.0,
    "realized_pnl": 200.0,
    "closed_at": "2024-12-19T11:00:00Z"
  }
}
```

### 5. 전략 관리

#### GET /v1/trading/strategies
거래 전략 목록을 조회합니다.

**쿼리 파라미터:**
- `strategy_type` (선택): 전략 타입 (TREND_FOLLOWING, MEAN_REVERSION)
- `is_active` (선택): 활성 상태 (true, false)

**응답:**
```json
{
  "success": true,
  "data": [
    {
      "id": "strategy_456",
      "name": "Trend Following Strategy",
      "strategy_type": "TREND_FOLLOWING",
      "description": "추세 추종 전략",
      "parameters": {
        "period": 20,
        "threshold": 0.02
      },
      "performance_metrics": {
        "total_return": 15.5,
        "sharpe_ratio": 1.8,
        "max_drawdown": 5.2,
        "win_rate": 65.0
      },
      "is_active": true,
      "created_at": "2024-12-19T09:00:00Z"
    }
  ]
}
```

#### GET /v1/trading/strategies/{strategy_id}/performance
전략의 성과 지표를 조회합니다.

**경로 파라미터:**
- `strategy_id`: 전략 ID

**쿼리 파라미터:**
- `period`: 기간 (1H, 1D, 1W, 1M)

**응답:**
```json
{
  "success": true,
  "data": {
    "strategy_id": "strategy_456",
    "period": "1D",
    "total_return": 2.5,
    "sharpe_ratio": 1.8,
    "max_drawdown": 1.2,
    "win_rate": 70.0,
    "profit_factor": 1.5,
    "total_trades": 25,
    "avg_trade_duration": 120.5,
    "calculated_at": "2024-12-19T10:30:00Z"
  }
}
```

### 6. 리스크 관리

#### GET /v1/trading/risk/portfolio
포트폴리오 리스크를 조회합니다.

**응답:**
```json
{
  "success": true,
  "data": {
    "total_exposure": 10000.0,
    "var_95": 500.0,
    "max_drawdown": 0.05,
    "concentration_risk": 0.3,
    "correlation_risk": 0.2,
    "liquidation_risk": "LOW",
    "recommendations": [
      "포지션 크기를 줄이세요",
      "상관관계가 높은 자산의 노출을 줄이세요"
    ]
  }
}
```

#### GET /v1/trading/risk/positions
포지션별 리스크를 조회합니다.

**응답:**
```json
{
  "success": true,
  "data": [
    {
      "position_id": "pos_123",
      "symbol": "BTCUSDT",
      "var_95": 100.0,
      "risk_level": "MEDIUM",
      "margin_ratio": 0.15,
      "liquidation_price": 40000.0,
      "recommendation": "현재 리스크 수준이 적절합니다"
    }
  ]
}
```

### 7. AI 에이전트 모니터링

#### GET /v1/ai/agents/status
AI 에이전트 상태를 조회합니다.

**응답:**
```json
{
  "success": true,
  "data": {
    "meta_controller": {
      "status": "active",
      "cpu_usage": 15.5,
      "memory_usage": 256.0,
      "last_update": "2024-12-19T10:30:00Z"
    },
    "market_regime_detector": {
      "status": "active",
      "cpu_usage": 8.2,
      "memory_usage": 128.0,
      "last_update": "2024-12-19T10:30:00Z"
    },
    "risk_manager": {
      "status": "active",
      "cpu_usage": 5.1,
      "memory_usage": 64.0,
      "last_update": "2024-12-19T10:30:00Z"
    }
  }
}
```

#### GET /v1/ai/agents/logs
AI 에이전트 로그를 조회합니다.

**쿼리 파라미터:**
- `agent_name` (선택): 에이전트 이름
- `level` (선택): 로그 레벨 (INFO, WARNING, ERROR)
- `limit` (선택): 반환할 데이터 수 (기본값: 100)

**응답:**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": "2024-12-19T10:30:00Z",
      "agent_name": "market_regime_detector",
      "level": "INFO",
      "message": "시장 국면 분석 완료",
      "details": {
        "regime_type": "TREND_UP",
        "confidence": 0.85
      }
    }
  ]
}
```

## 에러 코드

| 코드 | 설명 |
|------|------|
| `VALIDATION_ERROR` | 요청 데이터 검증 실패 |
| `AUTHENTICATION_ERROR` | 인증 실패 |
| `AUTHORIZATION_ERROR` | 권한 부족 |
| `NOT_FOUND` | 리소스를 찾을 수 없음 |
| `RATE_LIMIT_EXCEEDED` | 요청 한도 초과 |
| `INTERNAL_ERROR` | 내부 서버 오류 |
| `SERVICE_UNAVAILABLE` | 서비스 사용 불가 |

## 제한 사항

- **요청 한도**: 분당 1000회
- **응답 시간**: 평균 100ms 이하
- **데이터 보존**: 1년
- **최대 포지션**: 10개
- **최대 전략**: 50개

## WebSocket API

### 연결
```
ws://localhost:8000/ws
```

### 메시지 형식
```json
{
  "type": "subscribe",
  "channel": "market_data",
  "symbol": "BTCUSDT"
}
```

### 채널 목록
- `market_data`: 실시간 시장 데이터
- `trading_signals`: 거래 신호
- `position_updates`: 포지션 업데이트
- `risk_alerts`: 리스크 알림

## SDK 및 예제

### Python SDK
```python
from aitrading import TradingClient

client = TradingClient(api_key="your-api-key")

# 시장 국면 조회
regime = client.get_market_regime("BTCUSDT")

# 거래 신호 생성
signal = client.create_signal({
    "symbol": "BTCUSDT",
    "signal_type": "BUY",
    "confidence": 0.85,
    "entry_price": 45000.0
})
```

### JavaScript SDK
```javascript
import { TradingClient } from '@aitrading/sdk';

const client = new TradingClient('your-api-key');

// 포지션 조회
const positions = await client.getPositions();

// WebSocket 연결
const ws = client.connectWebSocket();
ws.on('market_data', (data) => {
    console.log('Market data:', data);
});
```

## 변경 이력

| 버전 | 날짜 | 변경 사항 |
|------|------|-----------|
| 1.0.0 | 2024-12-19 | 초기 API 릴리스 |

## 지원

- **문서**: https://docs.aitrading.com
- **지원**: support@aitrading.com
- **GitHub**: https://github.com/aitrading/ai-trading-system
