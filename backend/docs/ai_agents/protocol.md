# AI 에이전트 통신 프로토콜

**Version**: 1.0.0  
**Date**: 2024-12-19  
**Protocol**: Redis Pub/Sub + WebSocket

## 개요

AI 에이전트 간 통신을 위한 메시지 프로토콜과 데이터 형식을 정의합니다. Redis Pub/Sub를 기반으로 한 비동기 메시징과 WebSocket을 통한 실시간 통신을 지원합니다.

## 메시지 형식

### 기본 메시지 구조

```json
{
  "message_id": "uuid4",
  "timestamp": "2024-12-19T10:00:00.000Z",
  "sender": "agent_name",
  "receiver": "agent_name|broadcast",
  "message_type": "analysis_result|command|status|alert|heartbeat",
  "priority": "high|medium|low",
  "ttl": 300,
  "payload": {
    "data": "actual_message_data"
  },
  "metadata": {
    "version": "1.0.0",
    "correlation_id": "uuid4",
    "retry_count": 0
  }
}
```

### 필드 설명

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| message_id | string | ✓ | 고유 메시지 식별자 |
| timestamp | string | ✓ | 메시지 생성 시간 (ISO 8601) |
| sender | string | ✓ | 발신 에이전트 이름 |
| receiver | string | ✓ | 수신 에이전트 이름 또는 "broadcast" |
| message_type | string | ✓ | 메시지 타입 |
| priority | string | ✓ | 메시지 우선순위 |
| ttl | integer | ✓ | 메시지 생존 시간 (초) |
| payload | object | ✓ | 실제 메시지 데이터 |
| metadata | object | - | 추가 메타데이터 |

## 메시지 타입

### 1. Analysis Result (분석 결과)

시장 분석 결과를 전달하는 메시지입니다.

```json
{
  "message_id": "msg_001",
  "timestamp": "2024-12-19T10:00:00.000Z",
  "sender": "market_regime_detector",
  "receiver": "meta_controller",
  "message_type": "analysis_result",
  "priority": "high",
  "ttl": 300,
  "payload": {
    "analysis_type": "market_regime",
    "symbol": "BTCUSDT",
    "timeframe": "1h",
    "result": {
      "regime": "trending",
      "confidence": 0.85,
      "indicators": {
        "adx": 45.2,
        "hurst_exponent": 0.65,
        "bollinger_squeeze": 0.3
      }
    },
    "raw_data": {
      "price_data": [...],
      "volume_data": [...]
    }
  }
}
```

### 2. Command (명령)

에이전트에게 명령을 전달하는 메시지입니다.

```json
{
  "message_id": "msg_002",
  "timestamp": "2024-12-19T10:00:00.000Z",
  "sender": "meta_controller",
  "receiver": "risk_manager",
  "message_type": "command",
  "priority": "high",
  "ttl": 60,
  "payload": {
    "command": "update_risk_parameters",
    "parameters": {
      "max_position_size": 10000,
      "stop_loss_percentage": 0.02,
      "take_profit_percentage": 0.04
    },
    "execution_time": "2024-12-19T10:01:00.000Z"
  }
}
```

### 3. Status (상태)

에이전트 상태를 업데이트하는 메시지입니다.

```json
{
  "message_id": "msg_003",
  "timestamp": "2024-12-19T10:00:00.000Z",
  "sender": "vwap_analyzer",
  "receiver": "broadcast",
  "message_type": "status",
  "priority": "medium",
  "ttl": 60,
  "payload": {
    "agent_status": "active",
    "health_metrics": {
      "cpu_usage": 32.1,
      "memory_usage": 64.3,
      "uptime": 3600
    },
    "performance_metrics": {
      "signals_generated": 1250,
      "accuracy": 0.78,
      "avg_processing_time": 45.2
    }
  }
}
```

### 4. Alert (경고)

중요한 이벤트나 경고를 전달하는 메시지입니다.

```json
{
  "message_id": "msg_004",
  "timestamp": "2024-12-19T10:00:00.000Z",
  "sender": "risk_manager",
  "receiver": "broadcast",
  "message_type": "alert",
  "priority": "high",
  "ttl": 300,
  "payload": {
    "alert_type": "risk_limit_exceeded",
    "severity": "warning",
    "description": "Portfolio risk exceeds 80% of limit",
    "details": {
      "current_risk": 0.85,
      "risk_limit": 1.0,
      "affected_positions": ["BTCUSDT", "ETHUSDT"]
    },
    "recommended_actions": [
      "Reduce position sizes",
      "Close high-risk positions"
    ]
  }
}
```

### 5. Heartbeat (생존 신호)

에이전트의 생존을 확인하는 메시지입니다.

```json
{
  "message_id": "msg_005",
  "timestamp": "2024-12-19T10:00:00.000Z",
  "sender": "genetic_algorithm",
  "receiver": "meta_controller",
  "message_type": "heartbeat",
  "priority": "low",
  "ttl": 30,
  "payload": {
    "agent_status": "active",
    "last_activity": "2024-12-19T10:00:00.000Z",
    "processing_queue_size": 5
  }
}
```

## 채널 구조

### Redis Pub/Sub 채널

```
ai_agents.{agent_name}.inbox     # 특정 에이전트 수신 채널
ai_agents.{agent_name}.outbox    # 특정 에이전트 송신 채널
ai_agents.broadcast              # 브로드캐스트 채널
ai_agents.system                 # 시스템 메시지 채널
ai_agents.alerts                 # 경고 메시지 채널
```

### WebSocket 엔드포인트

```
/ws/ai-agents/{agent_name}       # 특정 에이전트 WebSocket
/ws/ai-agents/broadcast          # 브로드캐스트 WebSocket
/ws/ai-agents/system             # 시스템 WebSocket
```

## 메시지 라우팅

### 1. 직접 메시지

특정 에이전트에게 직접 전달되는 메시지입니다.

```
Sender → Redis Channel: ai_agents.{receiver}.inbox → Receiver
```

### 2. 브로드캐스트 메시지

모든 에이전트에게 전달되는 메시지입니다.

```
Sender → Redis Channel: ai_agents.broadcast → All Agents
```

### 3. 시스템 메시지

시스템 관리용 메시지입니다.

```
System → Redis Channel: ai_agents.system → All Agents
```

## 메시지 처리 규칙

### 1. 우선순위 처리

- **High**: 즉시 처리
- **Medium**: 일반 처리 큐
- **Low**: 백그라운드 처리

### 2. TTL (Time To Live)

메시지의 생존 시간을 초과하면 자동으로 삭제됩니다.

### 3. 재시도 메커니즘

메시지 처리 실패 시 최대 3회까지 재시도합니다.

```json
{
  "metadata": {
    "retry_count": 2,
    "max_retries": 3,
    "next_retry": "2024-12-19T10:00:30.000Z"
  }
}
```

### 4. 메시지 순서 보장

동일한 correlation_id를 가진 메시지들은 순서대로 처리됩니다.

## 에러 처리

### 에러 메시지 형식

```json
{
  "message_id": "msg_error_001",
  "timestamp": "2024-12-19T10:00:00.000Z",
  "sender": "system",
  "receiver": "sender_agent",
  "message_type": "error",
  "priority": "high",
  "ttl": 300,
  "payload": {
    "error_code": "PROCESSING_FAILED",
    "error_message": "Failed to process analysis result",
    "original_message_id": "msg_001",
    "error_details": {
      "exception": "ValueError",
      "stack_trace": "..."
    }
  }
}
```

### 에러 코드

| 코드 | 설명 |
|------|------|
| INVALID_MESSAGE_FORMAT | 잘못된 메시지 형식 |
| PROCESSING_FAILED | 메시지 처리 실패 |
| AGENT_UNAVAILABLE | 에이전트 사용 불가 |
| MESSAGE_EXPIRED | 메시지 만료 |
| PERMISSION_DENIED | 권한 부족 |

## 보안

### 1. 메시지 암호화

중요한 메시지는 AES-256으로 암호화됩니다.

```json
{
  "payload": {
    "encrypted": true,
    "encryption_key_id": "key_001",
    "data": "encrypted_payload_data"
  }
}
```

### 2. 메시지 서명

메시지 무결성을 보장하기 위해 HMAC-SHA256 서명을 사용합니다.

```json
{
  "signature": "hmac_sha256_signature",
  "signature_algorithm": "HMAC-SHA256"
}
```

### 3. 접근 제어

에이전트별 메시지 접근 권한을 관리합니다.

## 모니터링

### 1. 메시지 통계

```json
{
  "timestamp": "2024-12-19T10:00:00.000Z",
  "metrics": {
    "messages_sent": 1250,
    "messages_received": 1200,
    "messages_failed": 5,
    "avg_processing_time": 45.2,
    "queue_size": 10
  }
}
```

### 2. 에이전트 상태

```json
{
  "agent_name": "market_regime_detector",
  "status": "active",
  "last_heartbeat": "2024-12-19T10:00:00.000Z",
  "message_count": {
    "sent": 500,
    "received": 480,
    "failed": 2
  }
}
```

## 구현 예시

### Python 클라이언트

```python
import redis
import json
import uuid
from datetime import datetime

class AgentCommunicator:
    def __init__(self, agent_name, redis_url):
        self.agent_name = agent_name
        self.redis_client = redis.from_url(redis_url)
        self.pubsub = self.redis_client.pubsub()
        
    def send_message(self, receiver, message_type, payload, priority="medium"):
        message = {
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "sender": self.agent_name,
            "receiver": receiver,
            "message_type": message_type,
            "priority": priority,
            "ttl": 300,
            "payload": payload
        }
        
        channel = f"ai_agents.{receiver}.inbox"
        self.redis_client.publish(channel, json.dumps(message))
        
    def listen_for_messages(self):
        self.pubsub.subscribe(f"ai_agents.{self.agent_name}.inbox")
        self.pubsub.subscribe("ai_agents.broadcast")
        
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                self.process_message(data)
                
    def process_message(self, message):
        # 메시지 처리 로직
        pass
```

### JavaScript 클라이언트

```javascript
class AgentCommunicator {
  constructor(agentName, wsUrl) {
    this.agentName = agentName;
    this.ws = new WebSocket(`${wsUrl}/ai-agents/${agentName}`);
    this.ws.onmessage = (event) => this.processMessage(JSON.parse(event.data));
  }
  
  sendMessage(receiver, messageType, payload, priority = 'medium') {
    const message = {
      message_id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      sender: this.agentName,
      receiver: receiver,
      message_type: messageType,
      priority: priority,
      ttl: 300,
      payload: payload
    };
    
    this.ws.send(JSON.stringify(message));
  }
  
  processMessage(message) {
    // 메시지 처리 로직
  }
}
```

## 결론

이 통신 프로토콜은 AI 에이전트 간의 효율적이고 안전한 통신을 보장하며, 시스템의 확장성과 유지보수성을 고려하여 설계되었습니다. Redis Pub/Sub와 WebSocket을 활용하여 실시간 통신과 비동기 처리를 모두 지원합니다.