# 소스 코드 인덱스

## 개요
이 디렉토리는 프로젝트의 모든 소스 코드를 포함합니다.

## 디렉토리 구조

### 📁 `core/` - 핵심 유틸리티
- `config.py` - 설정 관리 (Pydantic 기반)
- `logger.py` - 로깅 시스템 (Rich 라이브러리)
- `database.py` - 데이터베이스 (SQLAlchemy + SQLite)

### 📁 `data/` - 데이터 처리
- `market_data.py` - Binance API 연동 및 시장 데이터 수집
- `indicators.py` - 기술적 지표 계산 (TA-Lib)

### 📁 `strategies/` - 거래 전략
- `base_strategy.py` - 전략 인터페이스 (추상 기본 클래스)
- `supertrend.py` - 슈퍼트렌드 기반 추세추종 전략
- `rsi_mean_reversion.py` - RSI 기반 평균회귀 전략

### 📄 `main.py` - 메인 실행 파일
- 트레이딩 봇 오케스트레이션
- 데이터 수집 → 지표 계산 → 전략 실행 → 거래 실행

## 주요 클래스

### Core 모듈
- `Config` - 설정 관리 클래스
- `setup_logging()` - 로깅 설정 함수
- `Trade`, `MarketData` - 데이터베이스 모델

### Data 모듈
- `MarketDataManager` - 시장 데이터 관리
- `calculate_supertrend()` - 슈퍼트렌드 지표 계산
- `calculate_rsi()` - RSI 지표 계산
- `calculate_sma()` - 이동평균선 계산

### Strategies 모듈
- `BaseStrategy` - 전략 기본 클래스
- `SupertrendStrategy` - 슈퍼트렌드 전략
- `RSIMeanReversionStrategy` - RSI 평균회귀 전략

## 사용 방법

### 실행
```bash
# 직접 실행
python src/main.py

# Docker 실행
docker-compose up --build -d
```

### 개발
1. **새 전략 추가**: `strategies/base_strategy.py` 상속
2. **새 지표 추가**: `data/indicators.py`에 함수 추가
3. **설정 변경**: `config/config.yaml` 수정

## 의존성
- `python-binance` - Binance API
- `pandas` - 데이터 처리
- `numpy` - 수치 계산
- `TA-Lib` - 기술적 지표
- `pydantic` - 설정 검증
- `rich` - 로깅
- `SQLAlchemy` - 데이터베이스
