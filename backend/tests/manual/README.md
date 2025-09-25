# 수동 테스트 및 검증

이 디렉토리는 AI 기반 암호화폐 거래 시스템의 수동 테스트 및 검증을 위한 테스트 파일들을 포함합니다.

## 테스트 파일들

### 1. test_manual_validation.py
**수동 검증 테스트**
- 헬스체크 테스트
- API 문서 접근성 테스트
- 인증 플로우 테스트
- 거래 엔드포인트 테스트
- 분석 엔드포인트 테스트
- 모니터링 엔드포인트 테스트
- 에러 처리 테스트
- CORS 헤더 테스트
- 보안 헤더 테스트
- 응답 시간 테스트
- 데이터 검증 테스트

### 2. test_user_acceptance.py
**사용자 수용 테스트 (UAT)**
- 사용자 등록 플로우 테스트
- 사용자 로그인 플로우 테스트
- 거래 대시보드 접근 테스트
- 시장 분석 접근 테스트
- 리스크 관리 접근 테스트
- AI 에이전트 모니터링 테스트
- 거래 주문 플로우 테스트
- 실시간 데이터 스트리밍 테스트
- 사용자 설정 테스트
- 사용자 관점에서의 에러 처리 테스트
- 사용자 경험 관점에서의 성능 테스트

### 3. test_integration_validation.py
**통합 검증 테스트**
- 데이터베이스 연결 테스트
- Redis 연결 테스트
- AI 에이전트 통합 테스트
- 거래 시스템 통합 테스트
- 분석 시스템 통합 테스트
- 리스크 관리 통합 테스트
- 모니터링 시스템 통합 테스트
- 데이터 플로우 통합 테스트
- API 일관성 테스트
- 에러 처리 통합 테스트
- 성능 통합 테스트
- 보안 통합 테스트

## 테스트 실행 방법

### 개별 테스트 실행
```bash
# 수동 검증 테스트
python -m pytest backend/tests/manual/test_manual_validation.py -v

# 사용자 수용 테스트
python -m pytest backend/tests/manual/test_user_acceptance.py -v

# 통합 검증 테스트
python -m pytest backend/tests/manual/test_integration_validation.py -v
```

### 모든 수동 테스트 실행
```bash
python -m pytest backend/tests/manual/ -v
```

### 특정 테스트 함수 실행
```bash
# 헬스체크 테스트만 실행
python -m pytest backend/tests/manual/test_manual_validation.py::test_manual_health_check -v

# 사용자 등록 플로우 테스트만 실행
python -m pytest backend/tests/manual/test_user_acceptance.py::test_user_registration_flow -v

# 데이터베이스 연결 테스트만 실행
python -m pytest backend/tests/manual/test_integration_validation.py::test_database_connectivity -v
```

## 테스트 설정

### 환경 변수
테스트를 실행하기 전에 다음 환경 변수들을 설정해야 합니다:

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/finance_db"
export REDIS_URL="redis://localhost:6379"
export SECRET_KEY="your-secret-key"
export API_BASE_URL="http://localhost:8000"
```

### 데이터베이스 설정
테스트를 실행하기 전에 데이터베이스가 실행 중이어야 합니다:

```bash
# PostgreSQL 시작
sudo systemctl start postgresql

# Redis 시작
sudo systemctl start redis
```

### 애플리케이션 시작
테스트를 실행하기 전에 애플리케이션이 실행 중이어야 합니다:

```bash
# 백엔드 서버 시작
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 테스트 결과 해석

### 성공 기준
- **수동 검증 테스트**: 90% 이상 성공률
- **사용자 수용 테스트**: 85% 이상 성공률
- **통합 검증 테스트**: 90% 이상 성공률

### 실패 허용
- **수동 검증 테스트**: 최대 1개 실패 허용
- **사용자 수용 테스트**: 최대 2개 실패 허용
- **통합 검증 테스트**: 최대 1개 실패 허용

### 응답 시간 기준
- **일반 API**: 1초 이내
- **사용자 경험**: 2초 이내
- **통합 테스트**: 1초 이내

## 테스트 데이터

### 테스트 사용자
- **이메일**: test@example.com
- **비밀번호**: testpassword123
- **이름**: Test User

### 테스트 주문 데이터
```json
{
  "symbol": "BTCUSDT",
  "side": "BUY",
  "amount": 0.001,
  "price": 50000,
  "order_type": "LIMIT"
}
```

### 테스트 설정 데이터
```json
{
  "theme": "dark",
  "notifications": {
    "email": true,
    "push": false
  }
}
```

## 문제 해결

### 일반적인 문제들

1. **연결 오류**
   - 데이터베이스가 실행 중인지 확인
   - Redis가 실행 중인지 확인
   - 애플리케이션이 실행 중인지 확인

2. **인증 오류**
   - 테스트 사용자가 생성되었는지 확인
   - JWT 토큰이 유효한지 확인

3. **타임아웃 오류**
   - 네트워크 연결 상태 확인
   - 서버 성능 상태 확인

4. **데이터 오류**
   - 데이터베이스 스키마가 최신인지 확인
   - 마이그레이션이 실행되었는지 확인

### 로그 확인
테스트 실행 중 문제가 발생하면 다음 로그를 확인하세요:

```bash
# 애플리케이션 로그
tail -f backend/logs/app.log

# 데이터베이스 로그
tail -f /var/log/postgresql/postgresql-*.log

# Redis 로그
tail -f /var/log/redis/redis-server.log
```

## 추가 정보

### 테스트 커버리지
이 테스트들은 다음 영역을 커버합니다:
- API 엔드포인트 기능성
- 사용자 인터페이스 접근성
- 시스템 통합성
- 성능 및 안정성
- 보안 및 인증
- 에러 처리 및 복구

### 테스트 자동화
이 테스트들은 CI/CD 파이프라인에서 자동으로 실행될 수 있습니다:

```yaml
# .github/workflows/manual-tests.yml
name: Manual Tests
on: [push, pull_request]
jobs:
  manual-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run manual tests
        run: |
          python -m pytest backend/tests/manual/ -v
```

### 테스트 확장
새로운 테스트를 추가하려면:

1. 적절한 테스트 파일을 선택하거나 새로 생성
2. 테스트 클래스를 상속받아 새로운 테스트 메서드 구현
3. `run_*_tests()` 메서드에 새 테스트 추가
4. pytest 테스트 함수 추가
5. README.md 업데이트
