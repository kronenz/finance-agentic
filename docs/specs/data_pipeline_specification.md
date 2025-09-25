# 데이터 파이프라인 명세서 (v1.0)

## 1. 개요
본 문서는 실시간 금융 데이터의 수집, 처리, 저장, 그리고 모델 전달까지의 전 과정을 담당하는 데이터 파이프라인의 구조와 흐름을 정의합니다. 파이프라인은 낮은 지연 시간, 높은 처리량, 확장성을 목표로 설계되었습니다.

## 2. 파이프라인 아키텍처
AI 에이전트 기반의 이벤트-주도 아키텍처를 채택합니다. 각 에이전트는 특정 작업을 수행하고 Redis Streams를 통해 메시지를 주고받으며 파이프라인을 구성합니다.

### 데이터 흐름도
```
[외부 거래소 API]
       |
       v (WebSocket/REST)
[1. DataCollectionAgent]
       |
       v (Raw Data)
[Redis Stream: "raw-market-data"]
       |
       v
[2. DataAnalysisAgent]
       |
       v (Processed Features)
[Redis Stream: "processed-features"]
       |
       +------------------+
       |                  |
       v                  v
[3. ML Agents]     [4. Database]
(Prediction/Signal)    (PostgreSQL)
```

## 3. 컴포넌트별 명세

### 3.1. 데이터 수집 (Data Ingestion)
- **담당 에이전트**: `DataCollectionAgent`
- **소스**: 주요 암호화폐 거래소 (Binance, Bybit 등)의 API (CCXT 라이브러리 활용)
- **방식**:
  - **실시간**: WebSocket을 사용하여 Ticker, Order Book 데이터 실시간 수신
  - **주기적**: REST API를 통해 1분 간격으로 OHLCV 데이터 폴링
- **출력**: 수집된 원본 데이터를 JSON 형식으로 직렬화하여 Redis Stream `raw-market-data`에 전송합니다.
- **장애 처리**: API 연결 실패 시 재시도 로직 및 로깅 수행.

### 3.2. 데이터 처리 및 특성 공학 (Processing & Feature Engineering)
- **담당 에이전트**: `DataAnalysisAgent`
- **입력**: `raw-market-data` 스트림 구독
- **처리 과정**:
  1. **데이터 정제**: 누락된 값 처리 및 이상치 탐지/보정
  2. **데이터 변환**: OHLCV, 거래량 등 기본 데이터 포맷 정규화
  3. **특성 공학**: `ta-lib` 등의 라이브러리를 사용하여 20개 이상의 기술적 지표 계산 (이동평균, RSI, MACD 등)
- **출력**: 계산된 특성을 포함한 처리 완료된 데이터를 `processed-features` 스트림에 전송합니다.

### 3.3. 데이터 저장 (Data Storage)
- **담당 에이전트**: `DatabaseAgent` (가칭, 또는 `DataAnalysisAgent`가 담당)
- **입력**: `processed-features` 스트림 구독
- **저장소**:
  - **실시간/캐시**: Redis. 최근 데이터 및 중간 계산 결과 저장
  - **영구 저장**: PostgreSQL (TimescaleDB 확장). 모든 시계열 데이터 및 특성, 모델 예측 결과, 거래 내역 등을 영구적으로 저장합니다.
- **목적**: 모델 학습, 백테스팅, 데이터 분석 및 시스템 복구를 위한 데이터 영속성 확보.

### 3.4. 데이터 소비 (Data Consumption)
- **소비자**: `PredictionAgent`, `SignalAgent` 등 ML 관련 에이전트
- **입력**: `processed-features` 스트림 구독
- **동작**: 스트림으로부터 실시간 특성 데이터를 받아 모델 추론을 수행하고, 그 결과를 다시 `prediction-results` 또는 `trading-signals`와 같은 새로운 스트림으로 전송합니다.

## 4. 데이터 포맷
- **메시지 포맷**: 모든 Redis Stream 메시지는 CloudEvents 표준을 따르는 JSON 형식으로 구성하여 메시지의 출처, 유형, 데이터를 명확히 합니다.
- **페이로드 예시 (`processed-features`):**
  ```json
  {
    "specversion": "1.0",
    "type": "com.finance.feature.processed",
    "source": "DataAnalysisAgent",
    "id": "uuid-...",
    "time": "2024-12-24T10:00:00Z",
    "data": {
      "symbol": "BTC/USDT",
      "timestamp": 1735034400,
      "open": 50000.0,
      "high": 50100.0,
      "low": 49900.0,
      "close": 50050.0,
      "volume": 100.5,
      "rsi": 55.2,
      "macd": 150.7,
      ...
    }
  }
  ```

## 5. 성능 요구사항

### 5.1. 지연 시간 (Latency)
- **데이터 수집**: 1초 이하
- **특성 계산**: 500ms 이하
- **모델 추론**: 100ms 이하
- **전체 파이프라인**: 2초 이하

### 5.2. 처리량 (Throughput)
- **데이터 수집**: 1000 TPS (Transactions Per Second)
- **특성 계산**: 500 TPS
- **모델 추론**: 100 TPS
- **데이터 저장**: 1000 TPS

### 5.3. 가용성 (Availability)
- **시스템 가동률**: 99.9% 이상
- **데이터 손실률**: 0.1% 이하
- **복구 시간**: 5분 이하

## 6. 장애 처리 및 복구

### 6.1. 장애 감지
- **헬스 체크**: 각 에이전트의 상태 모니터링
- **메트릭 모니터링**: 처리량, 지연시간, 에러율 추적
- **알림 시스템**: 임계값 초과 시 자동 알림

### 6.2. 복구 전략
- **자동 재시작**: 에이전트 장애 시 자동 재시작
- **데이터 복구**: Redis Streams의 메시지 지속성 활용
- **백업 시스템**: 대체 데이터 소스 활용

## 7. 모니터링 및 로깅

### 7.1. 메트릭 수집
- **Prometheus**: 시스템 메트릭 수집
- **Grafana**: 시각화 대시보드
- **커스텀 메트릭**: 비즈니스 로직별 메트릭

### 7.2. 로깅
- **구조화된 로깅**: JSON 형식 로그
- **로그 레벨**: DEBUG, INFO, WARN, ERROR
- **로그 집계**: ELK Stack 또는 Loki

## 8. 구현 계획

### 8.1. Phase 3.2 Week 2
- [ ] DataCollectionAgent 구현
- [ ] DataAnalysisAgent 구현
- [ ] Redis Streams 설정
- [ ] 기본 데이터 저장 구현

### 8.2. Phase 3.3 Week 3
- [ ] 고급 특성 엔지니어링
- [ ] 성능 최적화
- [ ] 모니터링 시스템 구축
- [ ] 장애 처리 메커니즘 구현

---

**문서 작성자**: Gemini CLI  
**작성일**: 2024-12-23  
**버전**: 1.0.0
