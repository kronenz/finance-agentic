# AI 에이전트 API 명세서

## 1. 개요 (Overview)

본 문서는 파이낸스 프로젝트의 AI 에이전트 간 통신을 위한 REST API 명세서를 정의합니다. 각 에이전트는 독립적인 마이크로서비스로 동작하며, 본 명세서에 정의된 API를 통해 상호작용합니다. 모든 통신은 비동기적으로 이루어지는 것을 원칙으로 합니다.

- 관련 문서: [AI 에이전트 통신 프로토콜](./ai_agent_communication_protocol.md)

## 2. 인증 및 권한 관리 (Authentication & Authorization)

모든 에이전트 간 API 요청은 JWT(JSON Web Token)를 이용한 인증을 거쳐야 합니다.

- **인증 (Authentication)**:
  - 각 에이전트는 시작 시 인증 서비스로부터 고유한 JWT를 발급받습니다.
  - API 요청 시 `Authorization` 헤더에 `Bearer <token>` 형태로 JWT를 포함하여 전송합니다.
  - API 서버는 요청 수신 시 JWT의 유효성을 검증합니다.

- **권한 관리 (Authorization)**:
  - JWT의 Payload에는 해당 에이전트의 역할(Role, 예: `DataAnalysisAgent`)이 포함됩니다.
  - 각 API 엔드포인트는 사전에 정의된 역할만 호출할 수 있도록 제한됩니다.
  - 권한이 없는 에이전트의 요청은 `403 Forbidden` 에러를 반환합니다.

## 3. API 버전 관리 (API Versioning)

API의 변경 및 업데이트를 관리하기 위해 URL 경로에 버전 정보를 포함합니다.

- **URL 형식**: `/api/v{version_number}/...`
- **현재 버전**: `v1`
- **예시**: `/api/v1/analysis/perform`

API의 호환성이 보장되지 않는 변경(Breaking Change)이 발생할 경우, 마이너 버전이 아닌 메이저 버전을 업데이트합니다. (예: `v1` -> `v2`)

## 4. 공통 요청/응답 형식

### 4.1. 성공 응답 (Success Response)

- **HTTP Status Code**: `200 OK` 또는 `202 Accepted`
- **Content-Type**: `application/json`

```json
{
  "status": "success",
  "data": {
    "task_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "message": "Task received successfully"
    // ... 기타 응답 데이터
  }
}
```

### 4.2. 에러 응답 (Error Response)

- **HTTP Status Code**: `4xx` 또는 `5xx`
- **Content-Type**: `application/json`

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "Required parameter 'symbol' is missing."
  }
}
```

## 5. 에이전트별 API 엔드포인트

### 5.1. Master Control Agent (오케스트레이션)

- **역할**: 모든 에이전트의 작업을 조율하고 전체 워크플로우를 관리합니다.

| Endpoint | 설명 | 요청 스키마 | 응답 스키마 |
| --- | --- | --- | --- |
| `POST /api/v1/tasks/dispatch` | 새로운 분석 또는 거래 작업을 시작하도록 각 에이전트에게 임무를 할당합니다. | `{ "task_type": "market_analysis", "params": { ... } }` | `{ "task_id": "...", "status": "dispatched" }` |

### 5.2. Data Collection Agent (데이터 수집)

- **역할**: 외부 API(거래소, 뉴스 등)로부터 시장 데이터를 수집합니다.

| Endpoint | 설명 | 요청 스키마 | 응답 스키마 |
| --- | --- | --- | --- |
| `POST /api/v1/data/collect` | 특정 데이터 수집을 요청합니다. | `{ "source": "binance", "data_type": "ohlcv", "params": { "symbol": "BTC/USDT", "timeframe": "1h" } }` | `{ "job_id": "...", "status": "pending" }` |
| `GET /api/v1/data/status/{job_id}` | 데이터 수집 작업의 상태를 확인합니다. | N/A | `{ "job_id": "...", "status": "completed", "location": "/data/..." }` |

### 5.3. Data Analysis Agent (데이터 분석)

- **역할**: 수집된 데이터를 기반으로 기술적, 통계적 분석을 수행합니다.

| Endpoint | 설명 | 요청 스키마 | 응답 스키마 |
| --- | --- | --- | --- |
| `POST /api/v1/analysis/perform` | 데이터 분석을 요청합니다. | `{ "analysis_type": "rsi", "data_path": "/data/...", "params": { "period": 14 } }` | `{ "analysis_id": "...", "status": "completed", "results": { ... } }` |

### 5.4. Market Monitoring Agent (시장 모니터링)

- **역할**: 실시간 시장 상황의 변화(급등/급락, 거래량 폭증 등)를 감지합니다.

| Endpoint | 설명 | 요청 스키마 | 응답 스키마 |
| --- | --- | --- | --- |
| `POST /api/v1/monitoring/events` | 감지된 시장 이벤트를 다른 에이전트에게 알립니다. | `{ "event_type": "price_surge", "symbol": "BTC/USDT", "details": { ... } }` | `{ "status": "event_received" }` |

### 5.5. Strategy Development Agent (전략 개발)

- **역할**: 분석된 데이터를 기반으로 새로운 거래 전략을 생성하거나 기존 전략을 최적화합니다.

| Endpoint | 설명 | 요청 스키마 | 응답 스키마 |
| --- | --- | --- | --- |
| `POST /api/v1/strategies/backtest` | 특정 전략의 백테스팅을 요청합니다. | `{ "strategy_code": "...", "data_range": { ... } }` | `{ "backtest_id": "...", "performance": { ... } }` |

### 5.6. Risk Management Agent (리스크 관리)

- **역할**: 거래 실행 전 리스크(예상 손실, 포트폴리오 비중 등)를 평가합니다.

| Endpoint | 설명 | 요청 스키마 | 응답 스키마 |
| --- | --- | --- | --- |
| `POST /api/v1/risk/assess` | 제안된 거래의 리스크를 평가합니다. | `{ "trade_details": { "symbol": "...", "side": "buy", "amount": "..." } }` | `{ "assessment_id": "...", "risk_level": "medium", "is_approved": true }` |

### 5.7. Trading Execution Agent (거래 실행)

- **역할**: 리스크 평가를 통과한 거래 주문을 실제 거래소에 전송합니다.

| Endpoint | 설명 | 요청 스키마 | 응답 스키마 |
| --- | --- | --- | --- |
| `POST /api/v1/orders/execute` | 거래 주문을 실행합니다. | `{ "exchange": "binance", "order_details": { ... } }` | `{ "order_id": "...", "status": "filled" }` |
| `GET /api/v1/orders/{order_id}` | 특정 주문의 상태를 조회합니다. | N/A | `{ "order_id": "...", "status": "filled", "details": { ... } }` |

### 5.8. Portfolio Management Agent (포트폴리오 관리)

- **역할**: 전체 자산 포트폴리오를 관리하고, 필요 시 리밸런싱을 제안합니다.

| Endpoint | 설명 | 요청 스키마 | 응답 스키마 |
| --- | --- | --- | --- |
| `GET /api/v1/portfolio/current` | 현재 포트폴리오 상태를 조회합니다. | N/A | `{ "assets": [ ... ], "total_value": "..." }` |
| `POST /api/v1/portfolio/rebalance` | 포트폴리오 리밸런싱을 제안/실행합니다. | `{ "target_allocations": { ... } }` | `{ "rebalance_id": "...", "status": "in_progress" }` |

### 5.9. User Interaction Agent (사용자 상호작용)

- **역할**: 중요한 이벤트나 거래 내역을 사용자에게 알립니다.

| Endpoint | 설명 | 요청 스키마 | 응답 스키마 |
| --- | --- | --- | --- |
| `POST /api/v1/notifications/send` | 사용자에게 알림을 전송합니다. | `{ "user_id": "...", "channel": "email", "message": "..." }` | `{ "notification_id": "...", "status": "sent" }` |

## 6. 에러 코드 (Error Codes)

| HTTP 상태 코드 | 에러 코드 | 설명 |
| --- | --- | --- |
| 400 Bad Request | `INVALID_PARAMETER` | 요청 파라미터가 잘못되었거나 누락되었습니다. |
| 401 Unauthorized | `UNAUTHENTICATED` | 인증되지 않은 요청입니다. 유효한 JWT가 필요합니다. |
| 403 Forbidden | `PERMISSION_DENIED` | 해당 리소스에 접근할 권한이 없습니다. |
| 404 Not Found | `NOT_FOUND` | 요청한 리소스를 찾을 수 없습니다. |
| 429 Too Many Requests | `RATE_LIMIT_EXCEEDED` | 단기간에 너무 많은 요청을 보냈습니다. |
| 500 Internal Server Error | `INTERNAL_SERVER_ERROR` | 서버 내부에서 처리 중 에러가 발생했습니다. |
| 503 Service Unavailable | `SERVICE_UNAVAILABLE` | 외부 서비스(거래소 등)의 문제로 요청을 처리할 수 없습니다. |

## 7. 상세 요청/응답 스키마

### 7.1. 데이터 수집 API 상세

#### POST /api/v1/data/collect
```json
{
  "source": "binance|coinbase|kraken",
  "data_type": "ohlcv|trades|orderbook",
  "params": {
    "symbol": "BTC/USDT",
    "timeframe": "1h|4h|1d",
    "start_time": "2024-12-01T00:00:00Z",
    "end_time": "2024-12-23T23:59:59Z"
  }
}
```

**응답**:
```json
{
  "status": "success",
  "data": {
    "job_id": "job_12345",
    "status": "pending",
    "estimated_completion": "2024-12-23T10:05:00Z"
  }
}
```

### 7.2. 분석 API 상세

#### POST /api/v1/analysis/perform
```json
{
  "analysis_type": "rsi|macd|bollinger_bands|moving_average",
  "data_path": "/data/btc_usdt_1h.csv",
  "params": {
    "period": 14,
    "smoothing": 2
  }
}
```

**응답**:
```json
{
  "status": "success",
  "data": {
    "analysis_id": "analysis_67890",
    "status": "completed",
    "results": {
      "rsi": 65.5,
      "macd": 120.3,
      "signal": "BUY",
      "confidence": 0.85
    }
  }
}
```

### 7.3. 거래 실행 API 상세

#### POST /api/v1/orders/execute
```json
{
  "exchange": "binance",
  "order_details": {
    "symbol": "BTCUSDT",
    "side": "BUY|SELL",
    "type": "LIMIT|MARKET",
    "quantity": 0.1,
    "price": 50000.0,
    "time_in_force": "GTC|IOC|FOK"
  }
}
```

**응답**:
```json
{
  "status": "success",
  "data": {
    "order_id": "order_abc123",
    "status": "filled",
    "executed_quantity": 0.1,
    "executed_price": 49995.0,
    "timestamp": "2024-12-23T10:00:05Z"
  }
}
```

## 8. Rate Limiting

각 에이전트는 API 호출 빈도를 제한하여 시스템 과부하를 방지합니다.

- **기본 제한**: 초당 100회 요청
- **버스트 허용**: 1초간 최대 200회 요청
- **복구 시간**: 1분 후 제한 해제

## 9. 모니터링 및 로깅

### 9.1. 로깅 요구사항
- 모든 API 요청/응답 로깅
- 에러 발생 시 상세 스택 트레이스
- 성능 메트릭 수집 (응답 시간, 처리량)

### 9.2. 모니터링 지표
- API 응답 시간 (P50, P95, P99)
- 에러율 (4xx, 5xx)
- 처리량 (RPS)
- 활성 연결 수

---

**문서 작성자**: Gemini CLI  
**작성일**: 2024-12-23  
**버전**: 1.0.0
