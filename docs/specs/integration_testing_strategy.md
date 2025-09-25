# 통합 테스트 전략 (v1.0)

## 1. 목적
본 문서는 금융 투자 시스템의 여러 컴포넌트(AI 에이전트, API 서버, 데이터베이스, 메시지 큐 등)가 유기적으로 연동하여 정확하게 동작하는지 검증하기 위한 통합 테스트 전략을 정의합니다.

## 2. 테스트 범위
- **AI 에이전트 간 통신**: Redis Streams를 통한 에이전트 간의 메시지 발행(Publish) 및 구독(Subscribe) 흐름 테스트
- **데이터 파이프라인 E2E**: 데이터 수집부터 처리, 저장, 모델 추론까지 이어지는 전체 데이터 흐름 테스트
- **API 및 백엔드 로직**: API 엔드포인트 호출 시 예상된 비즈니스 로직이 수행되고 데이터베이스 상태가 올바르게 변경되는지 검증
- **거래 실행 시뮬레이션**: `SignalAgent`가 생성한 신호를 `ExecutionAgent`가 받아 처리하는 가상 거래 실행 과정 테스트

## 3. 테스트 환경
- **구성**: `docker-compose.test.yml` 파일을 통해 별도의 테스트 환경을 구축합니다.
- **의존성**:
  - **메모리 DB**: 테스트용 Redis 인스턴스 사용
  - **테스트 DB**: 별도의 PostgreSQL 컨테이너를 사용하며, 테스트 실행 시마다 스키마를 초기화합니다.
  - **Mock/Fake 객체**: 외부 API(거래소)와 같이 제어가 불가능한 의존성은 Mock 객체나 Fake 서버로 대체합니다.

## 4. 테스트 전략 및 종류

### 4.1. 컴포넌트 통합 테스트 (Component Integration)
- **목표**: 개별 에이전트 또는 모듈 간의 상호작용을 검증합니다.
- **예시**:
  - `DataCollectionAgent`가 발행한 `raw-market-data` 메시지를 `DataAnalysisAgent`가 정상적으로 수신하여 처리하는지 테스트
  - `pytest`를 사용하여 테스트 케이스를 작성하고, 테스트용 Redis 클라이언트로 메시지를 직접 발행하거나 수신하여 검증합니다.

### 4.2. API 테스트 (API Testing)
- **목표**: FastAPI로 구현된 API 엔드포인트의 기능, 성능, 보안을 검증합니다.
- **도구**: `pytest`와 `HTTPX` 라이브러리 사용
- **검증 항목**:
  - **요청/응답 명세**: API 명세서에 따른 요청 형식과 응답 코드, 본문 구조 검증
  - **인증/인가**: JWT 토큰 기반의 인증 및 역할 기반의 인가 로직 검증
  - **데이터베이스 연동**: API 호출에 따른 데이터베이스 CRUD 작업의 정확성 검증

### 4.3. 엔드투엔드 테스트 (End-to-End Testing)
- **목표**: 사용자의 시나리오와 가장 유사한 전체 시스템의 흐름을 검증합니다.
- **시나리오 예시**:
  1. **데이터 수집 및 신호 생성**: Mock 거래소로부터 데이터를 수집하여 `DataCollectionAgent` 실행 -> `DataAnalysisAgent`가 특성 생성 -> `SignalAgent`가 '매수' 신호 생성
  2. **API를 통한 상태 확인**: `/api/v1/signals/latest` 엔드포인트를 호출하여 '매수' 신호가 생성되었는지 확인
  3. **거래 실행**: `ExecutionAgent`가 '매수' 신호를 수신하고 가상 거래를 실행했는지 데이터베이스에서 `trades` 테이블 확인
- **구현**: `pytest` 기반의 E2E 테스트 스크립트를 작성하여 전체 시나리오를 자동화합니다.

## 5. CI/CD 연동
- **통합**: GitHub Actions 워크플로우(`.github/workflows/ci.yml`)에 통합 테스트 실행 단계를 추가합니다.
- **트리거**: Pull Request 생성 또는 Main 브랜치에 Push될 때마다 자동으로 테스트를 실행합니다.
- **정책**: 통합 테스트를 통과하지 못한 코드는 Main 브랜치에 병합(Merge)될 수 없습니다.

## 6. 테스트 데이터 관리
- **Fixture**: `pytest`의 fixture 기능을 사용하여 테스트에 필요한 데이터(e.g., 사용자 정보, 초기 시장 데이터)를 사전에 생성합니다.
- **데이터 생성**: 테스트 시나리오에 필요한 특정 시장 상황(e.g., 급등, 급락) 데이터는 스크립트를 통해 동적으로 생성하여 Redis에 주입합니다.

## 7. 테스트 케이스 상세

### 7.1. AI 에이전트 통신 테스트
```python
def test_data_collection_to_analysis_flow():
    """데이터 수집 에이전트에서 분석 에이전트로의 메시지 전달 테스트"""
    # 1. DataCollectionAgent가 raw-market-data 스트림에 메시지 발행
    # 2. DataAnalysisAgent가 메시지 수신 및 처리
    # 3. processed-features 스트림에 결과 발행 확인
    pass

def test_signal_generation_flow():
    """신호 생성 에이전트의 메시지 처리 테스트"""
    # 1. processed-features 스트림에서 데이터 수신
    # 2. ML 모델을 통한 신호 생성
    # 3. trading-signals 스트림에 신호 발행 확인
    pass
```

### 7.2. API 통합 테스트
```python
def test_get_latest_signals_api():
    """최신 신호 조회 API 테스트"""
    # 1. 인증 토큰 발급
    # 2. /api/v1/signals/latest 엔드포인트 호출
    # 3. 응답 형식 및 데이터 검증
    pass

def test_trading_execution_api():
    """거래 실행 API 테스트"""
    # 1. 거래 신호 생성
    # 2. /api/v1/trades/execute 엔드포인트 호출
    # 3. 데이터베이스에 거래 기록 저장 확인
    pass
```

### 7.3. E2E 시나리오 테스트
```python
def test_complete_trading_cycle():
    """완전한 거래 사이클 테스트"""
    # 1. Mock 거래소 데이터 생성
    # 2. 데이터 수집 → 분석 → 신호 생성 → 거래 실행
    # 3. 전체 파이프라인 결과 검증
    pass
```

## 8. 성능 테스트

### 8.1. 부하 테스트
- **도구**: Locust 또는 Artillery
- **목표**: 동시 사용자 100명, 초당 1000 요청 처리
- **메트릭**: 응답 시간, 처리량, 에러율

### 8.2. 스트레스 테스트
- **목표**: 시스템 한계점 파악
- **시나리오**: 점진적 부하 증가
- **결과**: 최대 처리량 및 복구 시간 측정

## 9. 테스트 자동화

### 9.1. 테스트 실행 스크립트
```bash
#!/bin/bash
# integration_test.sh
docker-compose -f docker-compose.test.yml up -d
pytest tests/integration/ -v --cov=app
docker-compose -f docker-compose.test.yml down
```

### 9.2. 테스트 리포트
- **HTML 리포트**: pytest-html을 사용한 상세 리포트
- **커버리지 리포트**: pytest-cov를 사용한 코드 커버리지
- **성능 리포트**: 성능 테스트 결과 시각화

## 10. 구현 로드맵

### 10.1. Phase 3.2 Week 2
- [ ] 기본 통합 테스트 환경 구축
- [ ] AI 에이전트 간 통신 테스트 구현
- [ ] API 통합 테스트 구현
- [ ] 기본 E2E 테스트 시나리오 구현

### 10.2. Phase 3.3 Week 3
- [ ] 고급 E2E 테스트 시나리오 추가
- [ ] 성능 테스트 구현
- [ ] CI/CD 파이프라인 구축
- [ ] 테스트 자동화 완성

---

**문서 작성자**: Gemini CLI  
**작성일**: 2024-12-23  
**버전**: 1.0.0
