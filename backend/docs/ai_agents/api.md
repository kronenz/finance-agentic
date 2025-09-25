# AI 에이전트 API 문서

**Version**: 1.0.0  
**Date**: 2024-12-19  
**Base URL**: `/api/v1/ai-agents`

## 개요

AI 에이전트 시스템의 REST API 엔드포인트 문서입니다. 각 에이전트의 상태 조회, 제어, 설정 관리 기능을 제공합니다.

## 인증

모든 API 요청은 JWT 토큰을 사용한 인증이 필요합니다.

```http
Authorization: Bearer <jwt_token>
```

## 공통 응답 형식

### 성공 응답
```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2024-12-19T10:00:00Z"
}
```

### 에러 응답
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": {}
  },
  "timestamp": "2024-12-19T10:00:00Z"
}
```

## 에이전트 상태 관리

### 1. 전체 에이전트 상태 조회

```http
GET /api/v1/ai-agents/status
```

**응답**:
```json
{
  "success": true,
  "data": {
    "agents": [
      {
        "name": "meta_controller",
        "status": "active",
        "last_heartbeat": "2024-12-19T10:00:00Z",
        "cpu_usage": 45.2,
        "memory_usage": 128.5,
        "uptime": 3600
      },
      {
        "name": "market_regime_detector",
        "status": "active",
        "last_heartbeat": "2024-12-19T10:00:00Z",
        "cpu_usage": 32.1,
        "memory_usage": 64.3,
        "uptime": 3600
      }
    ],
    "system_health": "healthy"
  }
}
```

### 2. 특정 에이전트 상태 조회

```http
GET /api/v1/ai-agents/{agent_name}/status
```

**경로 매개변수**:
- `agent_name`: 에이전트 이름 (meta_controller, market_regime_detector, vwap_analyzer, volume_profile_analyzer, risk_manager, rl_optimizer, genetic_algorithm)

**응답**:
```json
{
  "success": true,
  "data": {
    "name": "market_regime_detector",
    "status": "active",
    "last_heartbeat": "2024-12-19T10:00:00Z",
    "cpu_usage": 32.1,
    "memory_usage": 64.3,
    "uptime": 3600,
    "configuration": {
      "confidence_threshold": 0.7,
      "update_interval": 60,
      "enabled_indicators": ["adx", "hurst", "bollinger"]
    },
    "performance_metrics": {
      "signals_generated": 1250,
      "accuracy": 0.78,
      "avg_processing_time": 45.2
    }
  }
}
```

## 에이전트 제어

### 3. 에이전트 시작/중지

```http
POST /api/v1/ai-agents/{agent_name}/control
```

**요청 본문**:
```json
{
  "action": "start|stop|restart",
  "reason": "Manual control request"
}
```

**응답**:
```json
{
  "success": true,
  "data": {
    "agent_name": "market_regime_detector",
    "action": "start",
    "status": "active",
    "message": "Agent started successfully"
  }
}
```

### 4. 에이전트 설정 업데이트

```http
PUT /api/v1/ai-agents/{agent_name}/config
```

**요청 본문**:
```json
{
  "confidence_threshold": 0.8,
  "update_interval": 30,
  "enabled_indicators": ["adx", "hurst", "bollinger", "rsi"]
}
```

**응답**:
```json
{
  "success": true,
  "data": {
    "agent_name": "market_regime_detector",
    "configuration": {
      "confidence_threshold": 0.8,
      "update_interval": 30,
      "enabled_indicators": ["adx", "hurst", "bollinger", "rsi"]
    },
    "message": "Configuration updated successfully"
  }
}
```

## 분석 결과 조회

### 5. 시장 국면 분석 결과

```http
GET /api/v1/ai-agents/market-regime/analysis
```

**쿼리 매개변수**:
- `symbol`: 거래 심볼 (선택사항)
- `timeframe`: 시간대 (1m, 5m, 15m, 1h, 4h, 1d)
- `limit`: 결과 수 제한 (기본값: 100)

**응답**:
```json
{
  "success": true,
  "data": {
    "current_regime": "trending",
    "confidence": 0.85,
    "indicators": {
      "adx": 45.2,
      "hurst_exponent": 0.65,
      "bollinger_squeeze": 0.3
    },
    "history": [
      {
        "timestamp": "2024-12-19T10:00:00Z",
        "regime": "trending",
        "confidence": 0.85,
        "indicators": {...}
      }
    ]
  }
}
```

### 6. VWAP 분석 결과

```http
GET /api/v1/ai-agents/vwap/analysis
```

**쿼리 매개변수**:
- `symbol`: 거래 심볼
- `timeframe`: 시간대
- `period`: 분석 기간 (기본값: 24h)

**응답**:
```json
{
  "success": true,
  "data": {
    "symbol": "BTCUSDT",
    "timeframe": "1h",
    "vwap": 45000.25,
    "price_deviation": 0.02,
    "volume_profile": {
      "poc": 45000.25,
      "vah": 45200.50,
      "val": 44800.00
    },
    "analysis": {
      "trend": "bullish",
      "strength": "strong",
      "support_resistance": [44800, 45200]
    }
  }
}
```

### 7. 거래량 프로파일 분석

```http
GET /api/v1/ai-agents/volume-profile/analysis
```

**응답**:
```json
{
  "success": true,
  "data": {
    "symbol": "BTCUSDT",
    "timeframe": "1h",
    "profile": {
      "poc_price": 45000.25,
      "vah_price": 45200.50,
      "val_price": 44800.00,
      "lvn_zones": [
        {"price": 44900, "volume": 0.1},
        {"price": 45100, "volume": 0.15}
      ]
    },
    "analysis": {
      "market_consensus": "strong",
      "value_area_ratio": 0.68,
      "profile_shape": "normal"
    }
  }
}
```

## 리스크 관리

### 8. 리스크 평가 결과

```http
GET /api/v1/ai-agents/risk/assessment
```

**응답**:
```json
{
  "success": true,
  "data": {
    "portfolio_risk": {
      "var_95": 2500.00,
      "var_99": 3500.00,
      "max_drawdown": 0.15,
      "sharpe_ratio": 1.85
    },
    "position_risks": [
      {
        "symbol": "BTCUSDT",
        "position_size": 1000.00,
        "var": 500.00,
        "risk_level": "medium"
      }
    ],
    "system_risks": {
      "liquidation_risk": "low",
      "correlation_risk": "medium",
      "concentration_risk": "low"
    }
  }
}
```

## 학습 및 최적화

### 9. RL 최적화 상태

```http
GET /api/v1/ai-agents/rl-optimizer/status
```

**응답**:
```json
{
  "success": true,
  "data": {
    "model_status": "training",
    "episode": 1250,
    "reward": 0.75,
    "loss": 0.12,
    "learning_rate": 0.001,
    "performance": {
      "accuracy": 0.78,
      "profit_factor": 1.45,
      "max_drawdown": 0.12
    }
  }
}
```

### 10. 유전 알고리즘 진화 상태

```http
GET /api/v1/ai-agents/genetic-algorithm/status
```

**응답**:
```json
{
  "success": true,
  "data": {
    "generation": 25,
    "population_size": 100,
    "best_fitness": 0.85,
    "average_fitness": 0.72,
    "diversity": 0.65,
    "best_strategies": [
      {
        "id": "strategy_001",
        "fitness": 0.85,
        "parameters": {...},
        "performance": {...}
      }
    ]
  }
}
```

## 로그 및 모니터링

### 11. 에이전트 로그 조회

```http
GET /api/v1/ai-agents/{agent_name}/logs
```

**쿼리 매개변수**:
- `level`: 로그 레벨 (DEBUG, INFO, WARNING, ERROR)
- `start_time`: 시작 시간
- `end_time`: 종료 시간
- `limit`: 로그 수 제한

**응답**:
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "timestamp": "2024-12-19T10:00:00Z",
        "level": "INFO",
        "message": "Market regime analysis completed",
        "details": {...}
      }
    ],
    "total_count": 1250,
    "has_more": true
  }
}
```

### 12. 성능 메트릭 조회

```http
GET /api/v1/ai-agents/metrics
```

**쿼리 매개변수**:
- `metric`: 메트릭 이름
- `timeframe`: 시간 범위
- `aggregation`: 집계 방식 (avg, sum, max, min)

**응답**:
```json
{
  "success": true,
  "data": {
    "metrics": [
      {
        "name": "signals_generated",
        "value": 1250,
        "timestamp": "2024-12-19T10:00:00Z",
        "trend": "increasing"
      }
    ]
  }
}
```

## 에러 코드

| 코드 | 설명 |
|------|------|
| AGENT_NOT_FOUND | 에이전트를 찾을 수 없음 |
| AGENT_OFFLINE | 에이전트가 오프라인 상태 |
| INVALID_CONFIG | 잘못된 설정 값 |
| OPERATION_FAILED | 작업 실행 실패 |
| INSUFFICIENT_PERMISSIONS | 권한 부족 |

## 제한 사항

- API 호출 제한: 분당 1000회
- 응답 크기 제한: 10MB
- 로그 조회 제한: 최대 1000개
- 실시간 데이터: WebSocket 연결 권장

## WebSocket 연결

실시간 데이터를 위해서는 WebSocket 연결을 사용하세요:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/ai-agents');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Real-time update:', data);
};
```