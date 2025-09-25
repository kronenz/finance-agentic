# AI 에이전트 통신 프로토콜 명세

**문서 버전:** 1.0
**작성일:** 2024-12-23

## 1. 개요

이 문서는 AI 에이전트 시스템 내 9개 에이전트 간의 효율적이고 안정적인 상호작용을 위한 통신 프로토콜을 정의한다. 모든 에이전트 간의 통신은 비동기 메시지 큐 방식을 기반으로 하며, 이는 시스템의 유연성, 확장성, 그리고 회복력을 보장하는 핵심 요소이다.

## 2. 메시지 큐 시스템: Redis Streams

### 2.1. 선택 사유

- **경량 및 고성능:** Redis는 인메모리 기반으로 매우 빠른 메시지 처리 속도를 제공하여 실시간성이 중요한 금융 애플리케이션에 적합하다.
- **데이터 지속성:** 데이터 스냅샷 및 AOF(Append Only File) 옵션을 통해 메시지 유실 방지가 가능하다.
- **소비자 그룹:** 여러 소비자가 동일한 스트림의 메시지를 중복 없이 분산 처리할 수 있는 강력한 소비자 그룹(Consumer Groups) 기능을 지원한다. 이는 특정 에이전트의 인스턴스를 여러 개 실행하여 수평적으로 확장할 때 유용하다.
- **프로젝트 통합성:** 현재 프로젝트 구성에 Redis가 이미 포함되어 있어 추가적인 인프라 설정 부담이 적다.

### 2.2. 스트림 설계

- **중앙 스트림 (Central Stream):** 모든 에이전트의 메시지는 단일 스트림인 `agent:messages`를 통해 전송된다.
- **메시지 필터링:** 각 에이전트는 메시지 내 `recipient_agent_id` 필드를 기준으로 자신에게 온 메시지만을 수신하여 처리한다. `broadcast`로 지정된 메시지는 모든 에이전트(또는 특정 그룹)가 수신할 수 있다.

## 3. 표준 메시지 형식

모든 메시지는 아래의 JSON 형식을 준수해야 한다.

```json
{
  "message_id": "string (UUID)",
  "correlation_id": "string (UUID)",
  "timestamp": "string (ISO 8601)",
  "sender_agent_id": "string",
  "recipient_agent_id": "string | broadcast",
  "task_name": "string",
  "payload": {},
  "status": "SUCCESS | FAILED | PENDING",
  "error": {
    "code": "string",
    "message": "string"
  }
}
```

- **message_id:** 각 메시지의 고유 식별자. 메시지 중복 처리를 위해 사용된다.
- **correlation_id:** 여러 메시지에 걸친 단일 트랜잭션 또는 워크플로우를 추적하기 위한 식별자.
- **timestamp:** 메시지 생성 시간.
- **sender_agent_id:** 메시지를 보낸 에이전트의 ID.
- **recipient_agent_id:** 메시지를 받을 에이전트의 ID. `broadcast`는 모든 에이전트에게 전송됨을 의미한다.
- **task_name:** 수행할 작업의 종류를 나타내는 명확한 이름 (예: `ANALYZE_MARKET_DATA`).
- **payload:** 작업 수행에 필요한 실제 데이터.
- **status:** 작업의 상태. 주로 응답 메시지에서 사용된다.
- **error:** 작업 실패 시 에러 정보를 담는 객체.

## 4. 주요 통신 흐름 (예시: 거래 실행)

1.  **데이터 수집 → 분석:**
    - `DataCollectionAgent`가 시장 데이터를 수집하여 `task_name: NEW_MARKET_DATA`로 `DataAnalysisAgent`에게 메시지 전송.

2.  **분석 → 전략:**
    - `DataAnalysisAgent`가 기술적 지표 등을 계산하고, `task_name: MARKET_ANALYSIS_RESULT`로 `StrategyPredictionAgent`에게 결과 전송.

3.  **전략 → 위험 관리:**
    - `StrategyPredictionAgent`가 거래 기회를 포착하여 `task_name: PROPOSE_TRADE`로 `RiskManagementAgent`에게 거래 제안 전송.

4.  **위험 관리 → 실행 (승인 시):**
    - `RiskManagementAgent`가 위험도를 평가하고 승인되면, `task_name: EXECUTE_TRADE`로 `ExecutionAgent`에게 주문 실행 요청.

5.  **실행 → 포트폴리오 및 마스터:**
    - `ExecutionAgent`가 주문 체결 후, `task_name: TRADE_CONFIRMATION`으로 `PortfolioManagementAgent`와 `MasterControlAgent`에게 체결 내역 전송.

## 5. 에러 처리 및 재시도 메커니즘

### 5.1. 메시지 처리 확인 (Acknowledgement)

- 각 에이전트는 메시지를 성공적으로 처리한 후, Redis의 `XACK` 명령어를 통해 메시지 처리를 명시적으로 확인해야 한다.
- 정해진 시간 내에 ACK가 수신되지 않으면, 해당 메시지는 다른 소비자에게 재전송될 수 있다.

### 5.2. 재시도 로직 (Retry Logic)

- 일시적인 오류(네트워크, API 제한 등)로 메시지 처리에 실패한 경우, 에이전트는 자체적으로 N회(예: 3회) 재시도를 수행한다.
- 재시도 간에는 Exponential Backoff 전략을 사용하여 시스템 부하를 줄인다.

### 5.3. 데드 레터 큐 (Dead Letter Queue, DLQ)

- 최종 재시도에도 불구하고 처리에 실패한 메시지는 `agent:dead_letter_queue` 스트림으로 이동된다.
- `MonitoringLoggingAgent`는 DLQ를 지속적으로 감시하며, 실패한 메시지에 대한 분석 및 알림(관리자에게)을 수행한다.

### 5.4. 멱등성 (Idempotency)

- 네트워크 문제 등으로 동일한 메시지가 중복 수신될 수 있다. 각 에이전트는 `message_id`를 확인하여 이미 처리한 메시지는 무시하고 다시 처리하지 않도록 멱등성을 보장해야 한다.

## 6. 메시지 타입별 상세 명세

### 6.1. 데이터 수집 관련 메시지

#### NEW_MARKET_DATA
```json
{
  "task_name": "NEW_MARKET_DATA",
  "payload": {
    "symbol": "BTCUSDT",
    "timestamp": "2024-12-23T10:00:00Z",
    "price": 50000.0,
    "volume": 1000.0,
    "source": "binance"
  }
}
```

#### MARKET_DATA_ERROR
```json
{
  "task_name": "MARKET_DATA_ERROR",
  "payload": {
    "error_type": "API_LIMIT_EXCEEDED",
    "retry_after": 60,
    "source": "binance"
  }
}
```

### 6.2. 분석 관련 메시지

#### MARKET_ANALYSIS_RESULT
```json
{
  "task_name": "MARKET_ANALYSIS_RESULT",
  "payload": {
    "symbol": "BTCUSDT",
    "indicators": {
      "rsi": 65.5,
      "macd": 120.3,
      "sma_20": 49500.0
    },
    "trend": "BULLISH",
    "confidence": 0.85
  }
}
```

### 6.3. 거래 관련 메시지

#### PROPOSE_TRADE
```json
{
  "task_name": "PROPOSE_TRADE",
  "payload": {
    "symbol": "BTCUSDT",
    "side": "BUY",
    "quantity": 0.1,
    "price": 50000.0,
    "strategy": "RSI_MEAN_REVERSION",
    "confidence": 0.75,
    "expected_return": 0.05
  }
}
```

#### EXECUTE_TRADE
```json
{
  "task_name": "EXECUTE_TRADE",
  "payload": {
    "order_id": "uuid",
    "symbol": "BTCUSDT",
    "side": "BUY",
    "quantity": 0.1,
    "price": 50000.0,
    "order_type": "LIMIT"
  }
}
```

#### TRADE_CONFIRMATION
```json
{
  "task_name": "TRADE_CONFIRMATION",
  "payload": {
    "order_id": "uuid",
    "symbol": "BTCUSDT",
    "side": "BUY",
    "quantity": 0.1,
    "executed_price": 49995.0,
    "executed_quantity": 0.1,
    "status": "FILLED",
    "timestamp": "2024-12-23T10:00:05Z"
  }
}
```

## 7. 성능 및 모니터링

### 7.1. 성능 지표
- **메시지 처리 지연시간**: 평균 50ms 이하
- **처리량**: 초당 1000개 메시지 이상
- **에러율**: 0.1% 이하
- **메시지 유실률**: 0% (Redis 지속성 보장)

### 7.2. 모니터링 포인트
- 각 에이전트의 메시지 처리량
- 메시지 처리 지연시간
- 에러 발생 빈도 및 유형
- DLQ 메시지 누적량
- Redis 메모리 사용량

## 8. 보안 고려사항

### 8.1. 메시지 암호화
- 민감한 거래 데이터는 AES-256으로 암호화
- 메시지 무결성 검증을 위한 HMAC 사용

### 8.2. 접근 제어
- 각 에이전트별 고유 인증 토큰
- 메시지 수신 권한 검증
- API 키 로테이션 정책

---

**문서 작성자**: Gemini CLI  
**작성일**: 2024-12-23  
**버전**: 1.0.0
