# ML 모델 아키텍처 상세 설계 (v1.0)

## 1. 개요
본 문서는 금융 투자 시스템의 핵심인 머신러닝 모델의 상세 아키텍처를 정의합니다. Phase 3.2에서는 시계열 예측과 거래 신호 생성을 위해 LSTM과 XGBoost 모델을 병행하여 사용하는 하이브리드 접근 방식을 채택합니다.

## 2. 모델 아키텍처

### 2.1. 모델 #1: LSTM (Long Short-Term Memory)
- **목적**: 주요 암호화폐의 미래 가격 변동성 및 추세 예측 (시계열 예측)
- **역할**: `PredictionAgent`가 이 모델을 사용하여 예측 결과를 생성하고, `StrategyAgent`가 이를 참고하여 거래 전략을 수립합니다.

#### 아키텍처
1. **입력 레이어 (Input Layer)**
   - **형태**: `(batch_size, sequence_length, num_features)`
   - `sequence_length`: 60 (과거 60분 데이터 사용)
   - `num_features`: 10+ (OHLCV, 이동평균, RSI, MACD, 볼린저 밴드 등)
2. **LSTM 레이어 (LSTM Layers)**
   - `LSTM Layer 1`: 128 units, `return_sequences=True`
   - `Dropout`: 0.2
   - `LSTM Layer 2`: 64 units, `return_sequences=False`
   - `Dropout`: 0.2
3. **출력 레이어 (Output Layer)**
   - `Dense Layer`: 32 units, `activation='relu'`
   - `Dense Layer`: 1 unit (예측 가격)

### 2.2. 모델 #2: XGBoost (Extreme Gradient Boosting)
- **목적**: 다양한 기술적 지표를 기반으로 '매수(Buy)', '매도(Sell)', '보유(Hold)' 신호 생성 (분류)
- **역할**: `SignalAgent`가 이 모델을 사용하여 구체적인 거래 신호를 생성합니다.

#### 아키텍처
- **종류**: Gradient Boosting Classifier
- **입력 피처**:
  - **기술적 지표**: 20개 이상의 지표 (RSI, MACD, Stochastic Oscillator, Williams %R 등)
  - **가격 정보**: 현재가, 변동률, 거래량 변동률
  - **LSTM 예측값**: LSTM 모델이 예측한 미래 가격 추세
- **출력**:
  - 다중 클래스 분류: `[2: 강력 매수, 1: 매수, 0: 보유, -1: 매도, -2: 강력 매도]`

## 3. 데이터 명세

### 3.1. 입력 데이터 (Features)
- **수집 주기**: 1분
- **데이터 소스**: `DataAnalysisAgent`가 처리한 실시간 데이터 스트림 (Redis)
- **주요 피처**:
  - `OHLCV` (시가, 고가, 저가, 종가, 거래량)
  - `Moving Averages` (5, 10, 20, 60분)
  - `RSI` (Relative Strength Index)
  - `MACD` (Moving Average Convergence Divergence)
  - `Bollinger Bands`
  - `Stochastic Oscillator`

### 3.2. 출력 데이터 (Labels)
- **LSTM**: 다음 15분 후의 종가
- **XGBoost**: 과거 데이터를 기반으로 레이블링된 최적의 거래 액션 (e.g., n분 후 가격이 x% 이상 오르면 '매수')

## 4. 학습 및 평가
- **학습 데이터**: 최소 1년 이상의 분 단위 데이터
- **데이터 분할**: Train (70%), Validation (15%), Test (15%)
- **평가 지표**:
  - **LSTM**: MAE (Mean Absolute Error), RMSE (Root Mean Square Error)
  - **XGBoost**: Accuracy, Precision, Recall, F1-Score, Confusion Matrix
- **백테스팅**: `BacktestingAgent`를 통해 과거 데이터로 실제 거래 상황을 시뮬레이션하여 모델의 수익률과 안정성을 검증합니다.

## 5. 모델 배포 및 서빙

### 5.1. 모델 저장
- **형식**: LSTM은 TensorFlow SavedModel, XGBoost는 pickle 파일
- **위치**: `/app/models/` 디렉토리
- **버전 관리**: MLflow를 사용한 모델 버전 관리

### 5.2. 실시간 추론
- **서빙 방식**: FastAPI 엔드포인트를 통한 REST API
- **배치 처리**: Redis Streams를 통한 실시간 데이터 처리
- **캐싱**: Redis를 사용한 예측 결과 캐싱

## 6. 모델 성능 모니터링

### 6.1. 실시간 메트릭
- **추론 지연시간**: 평균 100ms 이하
- **처리량**: 초당 1000개 요청 이상
- **정확도**: 70% 이상 유지

### 6.2. 모델 드리프트 감지
- **입력 데이터 분포 변화**: Kolmogorov-Smirnov 테스트
- **예측 성능 저하**: 정확도 임계값 모니터링
- **자동 재학습**: 성능 저하 시 자동 재학습 트리거

## 7. 구현 로드맵

### 7.1. Phase 3.2 Week 2
- [ ] LSTM 모델 구현 및 기본 훈련
- [ ] XGBoost 모델 구현 및 기본 훈련
- [ ] 모델 서빙 API 구현
- [ ] 기본 성능 테스트

### 7.2. Phase 3.3 Week 3
- [ ] 하이퍼파라미터 튜닝
- [ ] 모델 앙상블 구현
- [ ] 고급 특성 엔지니어링
- [ ] 백테스팅 시스템 구축

---

**문서 작성자**: Gemini CLI  
**작성일**: 2024-12-23  
**버전**: 1.0.0
