# Quickstart Guide: AI 기반 적응형 암호화폐 거래 시스템

## 시스템 개요

AI 기반 적응형 암호화폐 거래 시스템은 시장 국면을 자동으로 감지하고, 추세추종/평균회귀 전략을 동적으로 전환하여 자율적으로 거래를 실행하는 지능형 시스템입니다.

### 핵심 기능
- **시장 국면 자동 감지**: 머신러닝을 통한 추세/평균회귀 국면 실시간 분류
- **전략 동적 전환**: 시장 상황에 맞는 최적 전략 자동 선택
- **VWAP 분석**: 시장 참여자들의 평균 단가 기반 의사결정
- **거래량 프로파일**: POC/VA/LVN 분석을 통한 시장 합의 영역 파악
- **다층적 리스크 관리**: 개별/포트폴리오/시스템 레벨 리스크 통합 관리
- **자가 학습**: 강화학습과 유전 알고리즘을 통한 지속적 진화

## 시스템 아키텍처

### AI 에이전트 구성
```
메타-컨트롤러 (중앙 의사결정)
├── 시장 국면 분석 에이전트
├── 전략 분석 에이전트
├── 거래 실행 에이전트
├── 리스크 관리 에이전트
└── 데이터 수집 에이전트
```

### 데이터 흐름
```
실시간 시장 데이터 → AI 에이전트 분석 → 거래 신호 생성 → 리스크 검증 → 거래 실행
```

## 설치 및 설정

### 1. 시스템 요구사항
- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- 최소 8GB RAM
- SSD 저장공간 100GB+

### 2. 의존성 설치
```bash
# 백엔드 의존성
pip install -r backend/requirements.txt

# 프론트엔드 의존성
cd frontend
npm install
```

### 3. 환경 설정
```bash
# 환경 변수 설정
cp env.example .env

# 데이터베이스 초기화
python backend/scripts/init_db.py

# Redis 설정
redis-server redis.conf
```

### 4. 서비스 시작
```bash
# 백엔드 서버 시작
python backend/main.py

# 프론트엔드 개발 서버 시작
cd frontend
npm run dev
```

## 기본 사용법

### 1. 시스템 상태 확인
```bash
# API 상태 확인
curl http://localhost:8000/health

# 시장 국면 조회
curl http://localhost:8000/v1/trading/market-regime
```

### 2. 거래 신호 조회
```bash
# 최근 거래 신호 조회
curl "http://localhost:8000/v1/trading/signals?limit=10"

# 특정 심볼 신호 조회
curl "http://localhost:8000/v1/trading/signals?symbol=BTCUSDT"
```

### 3. VWAP 데이터 조회
```bash
# BTCUSDT VWAP 데이터 조회
curl "http://localhost:8000/v1/trading/vwap/BTCUSDT?timeframe=1h&limit=100"
```

### 4. 거래량 프로파일 조회
```bash
# BTCUSDT 거래량 프로파일 조회
curl "http://localhost:8000/v1/trading/volume-profile/BTCUSDT?timeframe=1h"
```

## 웹 인터페이스 사용법

### 1. 대시보드 접속
- URL: `http://localhost:3000`
- 기본 로그인: `admin@aitrading.com` / `password123`

### 2. 주요 화면
- **거래 신호 모니터링**: 실시간 거래 신호 및 성과 확인
- **시장 분석**: VWAP, 거래량 프로파일, 시장 국면 시각화
- **전략 관리**: 활성 전략 및 성과 지표 관리
- **리스크 모니터링**: 포지션 및 리스크 현황 실시간 확인

## API 사용 예제

### 1. 거래 신호 생성
```python
import requests

# 거래 신호 생성
signal_data = {
    "symbol": "BTCUSDT",
    "signal_type": "BUY",
    "confidence": 0.85,
    "entry_price": 45000.0,
    "stop_loss": 43000.0,
    "take_profit": 48000.0,
    "position_size": 1000.0,
    "strategy_id": "uuid-here"
}

response = requests.post(
    "http://localhost:8000/v1/trading/signals",
    json=signal_data,
    headers={"Authorization": "Bearer your-jwt-token"}
)
```

### 2. 시장 국면 분석
```python
# 현재 시장 국면 조회
response = requests.get("http://localhost:8000/v1/trading/market-regime")
regime = response.json()["data"]

print(f"현재 시장 국면: {regime['regime_type']}")
print(f"신뢰도: {regime['confidence_score']:.2f}")
```

### 3. 성과 지표 조회
```python
# 전략 성과 조회
strategy_id = "your-strategy-id"
response = requests.get(
    f"http://localhost:8000/v1/trading/strategies/{strategy_id}/performance",
    params={"period": "1D"}
)

metrics = response.json()["data"]
print(f"총 수익률: {metrics['total_return']:.2f}%")
print(f"샤프 지수: {metrics['sharpe_ratio']:.2f}")
print(f"최대 낙폭: {metrics['max_drawdown']:.2f}%")
```

## 테스트 시나리오

### 1. 기본 기능 테스트
```bash
# 1. 시스템 상태 확인
curl http://localhost:8000/health

# 2. 시장 데이터 수집 확인
curl "http://localhost:8000/v1/trading/vwap/BTCUSDT?timeframe=1h&limit=1"

# 3. 시장 국면 분석 확인
curl http://localhost:8000/v1/trading/market-regime

# 4. 거래 신호 생성 확인
curl -X POST http://localhost:8000/v1/trading/signals \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "signal_type": "BUY",
    "confidence": 0.8,
    "entry_price": 45000,
    "stop_loss": 43000,
    "take_profit": 48000,
    "position_size": 1000,
    "strategy_id": "test-strategy-id"
  }'
```

### 2. 통합 테스트
```bash
# 전체 워크플로우 테스트
python backend/tests/integration/test_full_workflow.py
```

### 3. 성능 테스트
```bash
# API 응답시간 테스트
python backend/tests/performance/test_api_response_time.py

# 동시 사용자 테스트
python backend/tests/performance/test_concurrent_users.py
```

## 문제 해결

### 1. 일반적인 문제
- **데이터베이스 연결 오류**: PostgreSQL 서비스 상태 확인
- **Redis 연결 오류**: Redis 서비스 상태 확인
- **API 응답 지연**: 서버 리소스 사용량 확인

### 2. 로그 확인
```bash
# 백엔드 로그
tail -f backend/logs/app.log

# 프론트엔드 로그
tail -f frontend/logs/app.log

# 시스템 로그
journalctl -u aitrading-backend -f
```

### 3. 성능 모니터링
```bash
# 시스템 리소스 확인
htop

# 데이터베이스 성능 확인
python backend/scripts/check_db_performance.py

# API 성능 확인
python backend/scripts/check_api_performance.py
```

## 보안 고려사항

### 1. API 인증
- JWT 토큰을 사용한 인증
- 토큰 만료시간: 24시간
- 리프레시 토큰: 7일

### 2. 데이터 암호화
- 전송 중 데이터: TLS 1.3
- 저장 데이터: AES-256 암호화
- API 키: 환경 변수로 관리

### 3. 접근 제어
- IP 화이트리스트 설정
- API 호출 제한: 분당 1000회
- 관리자 권한 분리

## 모니터링 및 알림

### 1. 시스템 모니터링
- CPU/메모리 사용률
- 데이터베이스 연결 수
- API 응답시간
- 에러 발생률

### 2. 거래 모니터링
- 거래 신호 생성 빈도
- 전략 성과 지표
- 리스크 지표 변화
- 시장 국면 변화

### 3. 알림 설정
- 이메일 알림
- 슬랙 알림
- SMS 알림 (긴급 상황)

## 다음 단계

### 1. 고급 설정
- 커스텀 전략 개발
- 리스크 파라미터 조정
- 알림 규칙 설정

### 2. 확장
- 추가 거래소 연동
- 새로운 AI 모델 통합
- 모바일 앱 개발

### 3. 최적화
- 성능 튜닝
- 비용 최적화
- 보안 강화

## 지원 및 문의

- **기술 지원**: support@aitrading.com
- **문서**: https://docs.aitrading.com
- **커뮤니티**: https://community.aitrading.com
- **GitHub**: https://github.com/aitrading/ai-trading-system
