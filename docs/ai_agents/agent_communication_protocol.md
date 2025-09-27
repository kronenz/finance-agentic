# AI 에이전트 통신 프로토콜

## 개요

AI 에이전트 간의 효율적이고 안정적인 통신을 위한 프로토콜 및 메시지 형식을 정의합니다.

## 통신 방식

### 1. RESTful API
**용도**: 동기적 명령 및 상태 조회
**특징**: 요청-응답 패턴, HTTP 기반

**엔드포인트 예시**:
```
GET /api/v1/agents/{agent_id}/status
POST /api/v1/agents/{agent_id}/command
GET /api/v1/agents/{agent_id}/metrics
```

### 2. WebSocket
**용도**: 실시간 데이터 스트리밍
**특징**: 양방향 통신, 지속적 연결

**연결 URL**:
```
ws://localhost:8000/ws/agents
```

### 3. Message Queue
**용도**: 비동기 통신 및 이벤트 처리
**특징**: 발행-구독 패턴, 높은 처리량

**큐 구성**:
- `market_data`: 시장 데이터
- `trading_signals`: 거래 신호
- `risk_alerts`: 리스크 알림
- `agent_commands`: 에이전트 명령

## 메시지 형식

### 기본 메시지 구조
```json
{
  "message_id": "uuid",
  "timestamp": "2024-01-01T00:00:00Z",
  "sender": "agent_id",
  "receiver": "agent_id",
  "message_type": "command|data|response|error",
  "payload": {},
  "metadata": {
    "priority": "low|medium|high|critical",
    "ttl": 300,
    "retry_count": 0
  }
}
```

### 메시지 타입별 스키마

#### 1. 시장 데이터 메시지
```json
{
  "message_type": "market_data",
  "payload": {
    "symbol": "BTCUSDT",
    "price": 45000.0,
    "volume": 1000.0,
    "timestamp": "2024-01-01T00:00:00Z",
    "data_type": "tick|ohlcv|orderbook"
  }
}
```

#### 2. 거래 신호 메시지
```json
{
  "message_type": "trading_signal",
  "payload": {
    "signal_id": "uuid",
    "symbol": "BTCUSDT",
    "signal_type": "BUY|SELL|HOLD",
    "confidence": 0.85,
    "entry_price": 45000.0,
    "stop_loss": 43000.0,
    "take_profit": 48000.0,
    "position_size": 1000.0,
    "strategy_id": "uuid",
    "market_regime_id": "uuid"
  }
}
```

#### 3. 리스크 알림 메시지
```json
{
  "message_type": "risk_alert",
  "payload": {
    "alert_id": "uuid",
    "alert_type": "position_limit|drawdown|correlation",
    "severity": "low|medium|high|critical",
    "message": "Position size exceeds limit",
    "data": {
      "current_value": 1500.0,
      "limit_value": 1000.0,
      "threshold": 1.5
    }
  }
}
```

#### 4. 에이전트 명령 메시지
```json
{
  "message_type": "agent_command",
  "payload": {
    "command": "start|stop|pause|resume|reconfigure",
    "parameters": {
      "strategy_id": "uuid",
      "risk_level": "low|medium|high"
    }
  }
}
```

## 에이전트별 통신 패턴

### 메타-컨트롤러
**수신 메시지**:
- 시장 국면 분석 결과
- VWAP 분석 결과
- 거래량 프로파일 분석 결과
- 리스크 평가 결과

**발송 메시지**:
- 거래 신호 생성 명령
- 전략 전환 명령
- 리스크 관리 조치

### 시장 국면 분석 에이전트
**수신 메시지**:
- 시장 데이터
- 분석 시작 명령

**발송 메시지**:
- 시장 국면 분석 결과
- 신뢰도 점수
- 변동성 수준

### VWAP 분석 에이전트
**수신 메시지**:
- 시장 데이터 (가격, 거래량)
- VWAP 계산 요청

**발송 메시지**:
- VWAP 값
- 표준편차 밴드
- 가격 편차 분석

### 거래량 프로파일 분석 에이전트
**수신 메시지**:
- 시장 데이터
- 프로파일 분석 요청

**발송 메시지**:
- POC, VAH, VAL 값
- LVN 구간 정보
- 거래량 분포

### 리스크 관리 에이전트
**수신 메시지**:
- 포지션 정보
- 시장 데이터
- 리스크 평가 요청

**발송 메시지**:
- 리스크 평가 결과
- 포지션 크기 권장
- 리스크 알림

## 에러 처리

### 에러 메시지 형식
```json
{
  "message_type": "error",
  "payload": {
    "error_code": "AGENT_UNAVAILABLE|INVALID_DATA|PROCESSING_ERROR",
    "error_message": "Agent is not responding",
    "details": {
      "agent_id": "market_regime_detector",
      "last_heartbeat": "2024-01-01T00:00:00Z"
    }
  }
}
```

### 재시도 정책
- **네트워크 오류**: 3회 재시도, 지수 백오프
- **처리 오류**: 1회 재시도
- **데이터 오류**: 재시도 없음, 에러 로그

### 타임아웃 설정
- **API 호출**: 5초
- **WebSocket 메시지**: 1초
- **큐 메시지**: 30초

## 보안

### 인증
- JWT 토큰 기반 인증
- 에이전트별 API 키
- IP 화이트리스트

### 암호화
- TLS 1.3 사용
- 메시지 페이로드 암호화
- 민감한 데이터 마스킹

### 접근 제어
- 역할 기반 접근 제어 (RBAC)
- 메시지 타입별 권한
- 에이전트별 접근 제한

## 모니터링

### 메트릭
- 메시지 처리량
- 응답 시간
- 에러 발생률
- 큐 길이

### 로깅
- 모든 메시지 로그
- 에러 로그
- 성능 로그
- 감사 로그

### 알림
- 에이전트 장애
- 메시지 처리 지연
- 큐 오버플로우
- 보안 위협

## 성능 최적화

### 메시지 압축
- gzip 압축 사용
- JSON 대신 MessagePack 고려
- 불필요한 필드 제거

### 배치 처리
- 여러 메시지 묶어서 처리
- 비동기 처리
- 캐싱 활용

### 로드 밸런싱
- 에이전트 인스턴스 분산
- 메시지 라우팅
- 장애 복구

