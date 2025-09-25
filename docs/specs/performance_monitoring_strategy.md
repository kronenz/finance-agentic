# 성능 모니터링 전략 (v1.0)

## 1. 목적
본 문서는 금융 투자 시스템의 안정성, 효율성, 신뢰성을 보장하기 위해 시스템의 상태와 성능을 실시간으로 측정하고 시각화하며, 이상 상황 발생 시 신속하게 대응하기 위한 모니터링 전략을 정의합니다.

## 2. 모니터링 스택 (Monitoring Stack)
- **메트릭 수집**: **Prometheus** - 시계열 데이터베이스 기반의 표준 모니터링 시스템
- **시각화 및 대시보드**: **Grafana** - Prometheus와 연동하여 메트릭을 시각화하는 대시보드 툴
- **로그 관리**: **Loki & Promtail** (선택적 도입) - 로그를 수집하고 메트릭과 연관 분석
- **알림**: **Alertmanager** - Prometheus와 통합되어 정의된 규칙에 따라 알림을 발송하는 시스템

### 아키텍처
```
+---------------------+      +-------------------+      +----------------+
|   Application /     |      |   Prometheus      |      |   Grafana      |
|   AI Agents         +------> (Metric Scraping) +------> (Dashboards)   |
| (FastAPI, Python)   |      |   (TSDB)          |      | (Visualization)|
+---------------------+      +---------+---------+      +----------------+
                                       |
                                       v
                               +-----------------+\
                               |  Alertmanager   |
                               |  (Alerting)     |
                               +-----------------+
```

## 3. 주요 모니터링 대상 및 메트릭

### 3.1. 시스템 인프라 메트릭 (Node Exporter)
- **CPU 사용률**: 컨테이너별, 노드별 CPU 사용량 및 부하
- **메모리 사용률**: 컨테이너별, 노드별 메모리 사용량 및 잔여량
- **디스크 I/O 및 사용량**: 데이터베이스 및 로그 저장소의 디스크 상태
- **네트워크 트래픽**: 컨테이너 간 네트워크 송수신량

### 3.2. 데이터 파이프라인 메트릭
- **담당 에이전트**: `DataCollectionAgent`, `DataAnalysisAgent`
- **메트릭**:
  - `pipeline_message_latency_seconds`: 메시지가 파이프라인 단계를 통과하는 데 걸리는 시간
  - `pipeline_message_throughput_total`: 단위 시간당 처리된 메시지 수
  - `redis_stream_pending_messages`: Redis Stream의 소비자 그룹에 쌓여있는 미처리 메시지 수 (병목 현상 감지)
  - `external_api_call_errors_total`: 외부 거래소 API 호출 실패 횟수

### 3.3. ML 모델 성능 메트릭
- **담당 에이전트**: `PredictionAgent`, `SignalAgent`
- **메트릭**:
  - `model_inference_latency_seconds`: 모델이 단일 요청을 추론하는 데 걸리는 시간
  - `model_prediction_accuracy`: (분류 모델) 예측 정확도
  - `model_prediction_mae`: (회귀 모델) Mean Absolute Error
  - `concept_drift_score`: 입력 데이터 분포 변화에 따른 모델 성능 저하 감지 지표

### 3.4. API 서버 메트릭 (FastAPI)
- **라이브러리**: `starlette-prometheus`
- **메트릭**:
  - `http_requests_total`: 엔드포인트별, HTTP 메소드별 총 요청 수
  - `http_requests_latency_seconds`: 요청 처리 시간 (Histogram/Summary)
  - `http_requests_in_progress`: 현재 처리 중인 동시 요청 수
  - `http_response_errors_total`: 5xx, 4xx 등 에러 응답 수

## 4. 구현 계획
1. **계측(Instrumentation)**:
   - 각 FastAPI 애플리케이션 및 AI 에이전트 코드에 Prometheus 클라이언트 라이브러리를 추가하여 `/metrics` 엔드포인트를 노출합니다.
   - 비즈니스 로직에 맞는 커스텀 메트릭(e.g., `trading_signals_total`)을 정의하고 코드를 추가합니다.
2. **설정(Configuration)**:
   - `prometheus.yml`에 각 서비스의 `/metrics` 엔드포인트 주소를 등록하여 주기적으로 메트릭을 수집(Scrape)하도록 설정합니다.
3. **대시보드 생성**:
   - Grafana에 Prometheus를 데이터 소스로 연결합니다.
   - 주요 메트릭을 시각화하는 대시보드를 생성합니다. (e.g., '종합 현황', '데이터 파이프라인', 'API 성능')
4. **알림 규칙 설정**:
   - `alert.rules.yml` 파일에 치명적인 상황에 대한 알림 규칙을 정의합니다.
   - **예시 규칙**:
     - API 에러율이 5분간 1% 이상일 경우
     - Redis Stream의 대기 메시지가 1,000개를 초과할 경우
     - 모델 예측 정확도가 60% 미만으로 떨어질 경우
   - Alertmanager를 설정하여 Slack, 이메일 등으로 알림을 발송합니다.

## 5. 대시보드 설계

### 5.1. 종합 현황 대시보드
- **시스템 상태**: 전체 서비스 가동률
- **핵심 메트릭**: 요청 수, 응답 시간, 에러율
- **리소스 사용률**: CPU, 메모리, 디스크
- **알림 현황**: 활성 알림 및 경고

### 5.2. 데이터 파이프라인 대시보드
- **처리량**: 메시지 처리 속도 및 지연시간
- **에러율**: 각 단계별 에러 발생률
- **큐 상태**: Redis Stream 대기 메시지 수
- **데이터 품질**: 유효한 데이터 비율

### 5.3. AI 모델 성능 대시보드
- **예측 정확도**: 실시간 정확도 추이
- **추론 지연시간**: 모델 실행 시간
- **신호 생성**: 거래 신호 생성 빈도
- **모델 드리프트**: 성능 저하 감지

## 6. 알림 규칙 상세

### 6.1. 치명적 알림 (Critical)
- **서비스 다운**: 주요 서비스 5분간 응답 없음
- **데이터 손실**: 메시지 처리 실패율 10% 이상
- **모델 실패**: 예측 정확도 50% 미만

### 6.2. 경고 알림 (Warning)
- **성능 저하**: 응답 시간 2초 이상
- **리소스 부족**: CPU 사용률 80% 이상
- **큐 백로그**: 대기 메시지 500개 이상

### 6.3. 정보 알림 (Info)
- **정상 복구**: 서비스 정상화
- **성능 개선**: 응답 시간 개선
- **새로운 신호**: 새로운 거래 신호 생성

## 7. 로깅 전략

### 7.1. 로그 레벨
- **DEBUG**: 상세한 디버깅 정보
- **INFO**: 일반적인 운영 정보
- **WARN**: 주의가 필요한 상황
- **ERROR**: 에러 발생 상황
- **CRITICAL**: 시스템 중단 위험

### 7.2. 로그 포맷
```json
{
  "timestamp": "2024-12-23T10:00:00Z",
  "level": "INFO",
  "service": "DataCollectionAgent",
  "message": "Market data collected",
  "metadata": {
    "symbol": "BTC/USDT",
    "count": 100,
    "duration_ms": 150
  }
}
```

## 8. 구현 로드맵

### 8.1. Phase 3.2 Week 2
- [ ] Prometheus 설정 및 메트릭 수집
- [ ] 기본 Grafana 대시보드 생성
- [ ] 핵심 알림 규칙 설정
- [ ] 로깅 시스템 구축

### 8.2. Phase 3.3 Week 3
- [ ] 고급 대시보드 및 시각화
- [ ] 자동화된 알림 시스템
- [ ] 성능 최적화 및 튜닝
- [ ] 모니터링 시스템 완성

## 9. 비용 및 리소스

### 9.1. 하드웨어 요구사항
- **Prometheus**: 2GB RAM, 100GB 디스크
- **Grafana**: 1GB RAM, 10GB 디스크
- **Alertmanager**: 512MB RAM, 1GB 디스크

### 9.2. 운영 비용
- **인프라 비용**: 월 $50-100 (클라우드 기준)
- **유지보수**: 주 2-3시간
- **알림 비용**: 월 $10-20 (Slack/이메일)

---

**문서 작성자**: Gemini CLI  
**작성일**: 2024-12-23  
**버전**: 1.0.0
