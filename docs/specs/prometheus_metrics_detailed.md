# Prometheus 메트릭 상세 설정

## 1. 개요

본 문서는 Phase 3.3 모니터링 시스템 구축을 위한 Prometheus 메트릭 수집 설정을 상세히 정의합니다. 애플리케이션, 인프라, 비즈니스 메트릭을 포함한 종합적인 모니터링을 목표로 합니다.

## 2. 메트릭 카테고리

### 2.1. 애플리케이션 메트릭

#### 2.1.1. HTTP 요청 메트릭
- `http_requests_total`: 총 HTTP 요청 수 (counter)
- `http_request_duration_seconds`: HTTP 요청 응답 시간 (histogram)
- `http_request_size_bytes`: HTTP 요청 크기 (histogram)
- `http_response_size_bytes`: HTTP 응답 크기 (histogram)
- `http_requests_in_flight`: 현재 처리 중인 요청 수 (gauge)

#### 2.1.2. API 엔드포인트별 메트릭
- `api_requests_total{endpoint, method, status}`: API별 요청 수
- `api_request_duration_seconds{endpoint, method}`: API별 응답 시간
- `api_errors_total{endpoint, method, error_type}`: API별 에러 수

#### 2.1.3. 인증 및 보안 메트릭
- `auth_login_attempts_total{result}`: 로그인 시도 수
- `auth_failed_logins_total{reason}`: 실패한 로그인 수
- `jwt_tokens_issued_total`: 발급된 JWT 토큰 수
- `jwt_tokens_expired_total`: 만료된 JWT 토큰 수

### 2.2. 데이터베이스 메트릭

#### 2.2.1. 연결 및 쿼리 메트릭
- `db_connections_active`: 활성 DB 연결 수 (gauge)
- `db_connections_idle`: 유휴 DB 연결 수 (gauge)
- `db_queries_total{query_type}`: 쿼리 수 (counter)
- `db_query_duration_seconds{query_type}`: 쿼리 실행 시간 (histogram)
- `db_errors_total{error_type}`: DB 에러 수 (counter)

#### 2.2.2. 트랜잭션 메트릭
- `db_transactions_total{status}`: 트랜잭션 수 (counter)
- `db_transaction_duration_seconds`: 트랜잭션 실행 시간 (histogram)
- `db_deadlocks_total`: 데드락 발생 수 (counter)

### 2.3. Redis 메트릭

#### 2.3.1. 캐시 성능 메트릭
- `redis_operations_total{operation}`: Redis 작업 수 (counter)
- `redis_operation_duration_seconds{operation}`: Redis 작업 시간 (histogram)
- `redis_hits_total`: 캐시 히트 수 (counter)
- `redis_misses_total`: 캐시 미스 수 (counter)
- `redis_hit_ratio`: 캐시 히트율 (gauge)

#### 2.3.2. 메모리 및 키 메트릭
- `redis_memory_usage_bytes`: Redis 메모리 사용량 (gauge)
- `redis_keys_total{type}`: Redis 키 수 (gauge)
- `redis_expired_keys_total`: 만료된 키 수 (counter)

### 2.4. AI 에이전트 메트릭

#### 2.4.1. 에이전트 상태 메트릭
- `ai_agents_active`: 활성 AI 에이전트 수 (gauge)
- `ai_agents_healthy`: 정상 AI 에이전트 수 (gauge)
- `ai_agent_messages_processed_total{agent_type}`: 처리된 메시지 수 (counter)
- `ai_agent_processing_duration_seconds{agent_type}`: 메시지 처리 시간 (histogram)

#### 2.4.2. ML 모델 메트릭
- `ml_predictions_total{model_type}`: ML 예측 수 (counter)
- `ml_prediction_duration_seconds{model_type}`: ML 예측 시간 (histogram)
- `ml_model_accuracy{model_type}`: ML 모델 정확도 (gauge)
- `ml_model_confidence{model_type}`: ML 모델 신뢰도 (histogram)

### 2.5. 비즈니스 메트릭

#### 2.5.1. 사용자 관련 메트릭
- `users_total`: 총 사용자 수 (gauge)
- `users_active_total`: 활성 사용자 수 (gauge)
- `users_registered_total`: 신규 등록 사용자 수 (counter)
- `users_logged_in_total`: 로그인한 사용자 수 (counter)

#### 2.5.2. 구독 관련 메트릭
- `subscriptions_total{plan_type}`: 구독 수 (gauge)
- `subscriptions_created_total{plan_type}`: 신규 구독 수 (counter)
- `subscriptions_cancelled_total{plan_type}`: 취소된 구독 수 (counter)
- `subscription_revenue_total{plan_type}`: 구독 수익 (counter)

#### 2.5.3. 거래 관련 메트릭
- `trades_total{side}`: 거래 수 (counter)
- `trade_volume_total{side}`: 거래량 (counter)
- `trade_value_total{side}`: 거래 가치 (counter)
- `trading_signals_generated_total{signal_type}`: 생성된 거래 신호 수 (counter)

### 2.6. 시스템 메트릭

#### 2.6.1. 리소스 사용량 메트릭
- `system_cpu_usage_percent`: CPU 사용률 (gauge)
- `system_memory_usage_bytes`: 메모리 사용량 (gauge)
- `system_disk_usage_bytes{device}`: 디스크 사용량 (gauge)
- `system_network_bytes_total{interface, direction}`: 네트워크 트래픽 (counter)

#### 2.6.2. 프로세스 메트릭
- `process_cpu_seconds_total`: 프로세스 CPU 사용 시간 (counter)
- `process_memory_bytes`: 프로세스 메모리 사용량 (gauge)
- `process_open_fds`: 열린 파일 디스크립터 수 (gauge)
- `process_threads`: 스레드 수 (gauge)

## 3. 메트릭 수집 설정

### 3.1. Prometheus 설정 파일

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'finance-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s
    
  - job_name: 'finance-frontend'
    static_configs:
      - targets: ['frontend:3000']
    metrics_path: '/metrics'
    scrape_interval: 15s
    
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
    scrape_interval: 30s
    
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
    scrape_interval: 30s
    
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 30s
```

### 3.2. 메트릭 수집 주기

- **고빈도 메트릭**: 10초 (HTTP 요청, 응답 시간)
- **중빈도 메트릭**: 30초 (시스템 리소스, DB 연결)
- **저빈도 메트릭**: 1분 (비즈니스 메트릭, 사용자 수)

## 4. 메트릭 라벨링 전략

### 4.1. 공통 라벨
- `service`: 서비스 이름 (finance-backend, finance-frontend)
- `environment`: 환경 (development, staging, production)
- `version`: 애플리케이션 버전

### 4.2. HTTP 메트릭 라벨
- `method`: HTTP 메서드 (GET, POST, PUT, DELETE)
- `endpoint`: API 엔드포인트
- `status_code`: HTTP 상태 코드
- `user_id`: 사용자 ID (선택적)

### 4.3. 데이터베이스 메트릭 라벨
- `database`: 데이터베이스 이름
- `table`: 테이블 이름
- `operation`: 작업 유형 (SELECT, INSERT, UPDATE, DELETE)

### 4.4. AI 에이전트 메트릭 라벨
- `agent_type`: 에이전트 유형 (data_collection, data_analysis, prediction)
- `agent_id`: 에이전트 ID
- `message_type`: 메시지 유형

## 5. 메트릭 저장 및 보존

### 5.1. 보존 정책
- **고해상도 데이터**: 1일 (1분 간격)
- **중해상도 데이터**: 7일 (5분 간격)
- **저해상도 데이터**: 30일 (1시간 간격)
- **장기 보존**: 1년 (1일 간격)

### 5.2. 압축 설정
- **압축 알고리즘**: LZ4
- **압축 레벨**: 3
- **압축 주기**: 2시간

## 6. 메트릭 검증

### 6.1. 데이터 품질 검증
- 메트릭 값의 범위 검증
- 라벨 값의 유효성 검증
- 메트릭 수집 간격 검증

### 6.2. 성능 영향 검증
- 메트릭 수집으로 인한 성능 저하 측정
- 메모리 사용량 증가 측정
- 네트워크 대역폭 사용량 측정
