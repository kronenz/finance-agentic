# 시작하기 가이드

## 🚀 빠른 시작

### 1. 시스템 요구사항

- Python 3.9 이상
- Git
- 최소 2GB RAM
- 안정적인 인터넷 연결

### 2. 설치 및 설정

```bash
# 저장소 클론
git clone <repository-url>
cd finance

# 설정 스크립트 실행
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 3. 환경 변수 설정

`.env` 파일을 편집하여 실제 API 키를 입력하세요:

```bash
# 바이낸스 API 키 (테스트넷)
BINANCE_API_KEY=your_actual_api_key_here
BINANCE_SECRET_KEY=your_actual_secret_key_here

# 기타 설정
LOG_LEVEL=INFO
DEFAULT_LEVERAGE=5
```

### 4. 시스템 실행

```bash
# 개발 모드
python src/main.py

# 또는 Docker 사용
docker-compose up -d
```

## 📊 시스템 모니터링

### 로그 확인
```bash
# 실시간 로그
tail -f logs/trading.log

# 특정 전략 로그
tail -f logs/strategy.log
```

### 데이터베이스 확인
```bash
# SQLite 데이터베이스 접근
sqlite3 data/trading.db

# 거래 기록 조회
SELECT * FROM trades ORDER BY timestamp DESC LIMIT 10;
```

## 🔧 개발 가이드

### 브랜치 전략

- `dev`: 개발 브랜치 (기능 개발)
- `stage`: 스테이징 브랜치 (통합 테스트)
- `prod`: 프로덕션 브랜치 (실제 거래)

### 새로운 기능 개발

1. `dev` 브랜치에서 작업
2. 테스트 작성 및 실행
3. Pull Request 생성
4. 코드 리뷰 후 `stage` 브랜치로 머지
5. 스테이징 테스트 통과 후 `prod` 브랜치로 배포

### 배포

```bash
# 개발 환경 배포
./scripts/deploy.sh dev

# 스테이징 환경 배포
./scripts/deploy.sh stage

# 프로덕션 환경 배포
./scripts/deploy.sh prod
```

## 📈 전략 설정

### 슈퍼트렌드 전략

`config/config.yaml`에서 설정:

```yaml
strategies:
  supertrend:
    enabled: true
    atr_period: 10
    atr_multiplier: 3.0
```

### RSI 평균회귀 전략

```yaml
strategies:
  rsi_mean_reversion:
    enabled: true
    rsi_period: 14
    oversold_threshold: 30
    overbought_threshold: 70
    hold_days: 10
```

## ⚠️ 주의사항

### Phase 1 제한사항

- 테스트넷만 지원 (실제 자금 사용 안함)
- 단순한 전략만 구현
- 기본적인 리스크 관리만 제공

### 보안

- API 키는 절대 공개하지 마세요
- `.env` 파일은 Git에 커밋하지 마세요
- 프로덕션 환경에서는 추가 보안 조치가 필요합니다

## 🆘 문제 해결

### 일반적인 문제

1. **API 연결 실패**
   - API 키가 올바른지 확인
   - 네트워크 연결 상태 확인
   - 바이낸스 서버 상태 확인

2. **데이터베이스 오류**
   - `data/` 디렉토리 권한 확인
   - 디스크 공간 확인

3. **전략 신호 없음**
   - 시장 데이터 수집 상태 확인
   - 전략 설정 확인
   - 로그에서 오류 메시지 확인

### 로그 레벨 조정

```yaml
logging:
  level: "DEBUG"  # DEBUG, INFO, WARNING, ERROR
```

## 📚 추가 자료

- [Phase 1 명세서](specs/phase1_minimal_trading.md)
- [아키텍처 문서](architecture/)
- [API 문서](api/)

## 🤝 기여하기

1. 이슈 생성 또는 기존 이슈 확인
2. `dev` 브랜치에서 기능 개발
3. 테스트 작성 및 실행
4. Pull Request 생성
5. 코드 리뷰 후 머지

## 📞 지원

- 이슈 트래커: GitHub Issues
- 문서: 프로젝트 Wiki
- 커뮤니티: GitHub Discussions
