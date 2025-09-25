# ML Strategy Specification

## 1. 개요

본 문서는 금융 투자 AI 에이전트의 머신러닝(ML) 모델 개발 전략을 정의한다. 목표는 다양한 거래 전략에 적합한 ML 모델을 구축하고, 데이터 처리, 모델 선택, 학습 및 평가 프로세스를 체계화하여 높은 성능과 안정성을 갖춘 예측 모델을 개발하는 것이다.

## 2. 거래 전략별 ML 모델 요구사항 분석

각 거래 전략의 특성에 맞춰 ML 모델의 역할과 요구사항을 다음과 같이 정의한다.

| 거래 전략 | 모델 목표 | 예측 대상 | 주요 고려사항 |
| --- | --- | --- | --- |
| **RSI Mean Reversion** | 과매수/과매도 구간에서의 반전 시점 예측 정확도 향상 | 추세 반전 확률 또는 시점 | RSI 지표의 한계를 보완할 수 있는 추가 피처 필요 |
| **Supertrend** | 추세의 시작과 끝을 더 정확하게 예측 | 추세 지속/전환 시그널 | 변동성이 큰 시장에서의 잦은 거짓 신호(Whipsaw) 방지 |
| **Volatility Breakout** | 변동성 폭발 시점 및 방향 예측 | 지정된 기간 내 가격 돌파 확률 및 방향 | 거래량, 시장 심리 등 변동성 관련 피처 중요 |
| **Arbitrage** | 거래소 간 가격 차이 발생 가능성 예측 | 차익 발생 확률 및 예상 수익률 | 실시간 데이터 처리 및 빠른 예측 속도 요구 |

## 3. 데이터 전처리 및 특성 엔지니어링 전략

### 3.1. 데이터 소스

- **시계열 데이터**: OHLCV (Open, High, Low, Close, Volume)
- **기술적 지표**: 이동평균선(SMA, EMA), MACD, Bollinger Bands, ATR 등
- **오더북 데이터**: 매수/매도 호가 및 수량
- **온체인 데이터**: 트랜잭션 볼륨, 활성 주소 수 등 (암호화폐의 경우)
- **대체 데이터**: 뉴스 헤드라인, 소셜 미디어 감성 지수 등 (필요시)

### 3.2. 데이터 전처리

- **결측치 처리**: Time-based forward-fill 또는 backward-fill 적용
- **이상치 탐지 및 처리**: IQR(Interquartile Range) 또는 Z-score를 이용한 탐지 및 제거/대체
- **정규화/표준화**:
    - **StandardScaler**: 대부분의 피처에 적용하여 평균 0, 분산 1로 조정
    - **MinMaxScaler**: 0과 1 사이로 스케일링이 필요할 경우 (예: 신경망 모델 입력)

### 3.3. 특성 엔지니어링

- **기본 피처**:
    - **Lag Features**: 과거 N개의 시점 데이터 (예: `price(t-1)`, `price(t-2)`)
    - **Moving Averages**: 단기, 중기, 장기 이동평균 및 이들 간의 비율/차이
    - **Volatility Features**: ATR, 표준편차 등 변동성 지표
- **고급 피처**:
    - **Time-based Features**: 요일, 시간대 등 주기적 특성
    - **Interaction Features**: 거래량과 가격 변동폭의 곱 등
    - **Fractal Features**: 프랙탈 차원 분석을 통한 시장 복잡성 측정

## 4. 모델 선택 및 하이퍼파라미터 튜닝 전략

### 4.1. 후보 모델

- **Baseline Models**:
    - **Logistic/Linear Regression**: 간단하고 해석이 용이하여 기본 성능 측정에 사용
- **Tree-based Models**:
    - **Random Forest**: 다수 결정 트리의 앙상블로 과적합 방지 및 높은 성능
    - **LightGBM/XGBoost**: Gradient Boosting 기반으로 빠르고 정확한 예측 능력
- **Sequence Models**:
    - **LSTM/GRU**: 시계열 데이터의 장기 의존성 학습에 특화된 딥러닝 모델

### 4.2. 모델 선택

- **Walk-Forward Validation**: 시계열 데이터의 특성을 고려하여 순차적으로 훈련/검증 데이터를 나누어 모델 성능을 비교한다.
- **점진적 복잡도 증가**: 간단한 모델(Baseline)부터 시작하여 점차 복잡한 모델(Tree-based, Sequence)로 실험을 확장하며 성능 향상 폭을 측정한다.

### 4.3. 하이퍼파라미터 튜닝

- **Grid Search**: 제한된 탐색 공간에서 최적의 조합을 찾을 때 사용
- **Random Search**: 넓은 탐색 공간에서 효율적으로 준수한 조합을 찾을 때 사용
- **Bayesian Optimization (Optuna, Hyperopt)**: 순차적으로 이전 탐색 결과를 활용하여 다음 탐색 지점을 추천받아 최적의 하이퍼파라미터를 효율적으로 탐색 (주력으로 사용)

## 5. 모델 성능 평가 기준

### 5.1. 분류 모델 평가 지표

- **Accuracy**: 전체 예측 중 올바르게 예측한 비율
- **Precision**: '매수'로 예측한 것 중 실제로 상승한 비율
- **Recall**: 실제 상승한 것 중 모델이 '매수'로 예측한 비율
- **F1-Score**: 정밀도와 재현율의 조화 평균
- **AUC-ROC**: 모델이 양성 클래스와 음성 클래스를 얼마나 잘 구별하는지

### 5.2. 회귀 모델 평가 지표

- **MAE (Mean Absolute Error)**: 예측 오차의 절대값 평균
- **MSE (Mean Squared Error)**: 예측 오차의 제곱 평균
- **RMSE (Root Mean Squared Error)**: MSE에 제곱근을 취한 값
- **R-squared**: 모델이 데이터의 분산을 얼마나 잘 설명하는지

### 5.3. 금융 성과 평가 지표

- **Total PnL**: 총 손익
- **Sharpe Ratio**: 위험 대비 수익률
- **Sortino Ratio**: 하방 위험 대비 수익률
- **Maximum Drawdown**: 최대 낙폭
- **Win/Loss Ratio**: 수익을 낸 거래의 비율
- **Profit Factor**: 총 수익을 총 손실로 나눈 값

## 6. 모델 배포 및 모니터링

### 6.1. 모델 배포 전략

- **A/B Testing**: 기존 전략과 새 모델의 성과를 비교
- **Paper Trading**: 실시간 데이터로 모의 거래 실행
- **Gradual Rollout**: 소액부터 점진적으로 자본 투입

### 6.2. 모델 모니터링

- **성능 지표 모니터링**: 정확도, 수익률, 드로우다운 등
- **데이터 드리프트 감지**: 입력 데이터 분포 변화 모니터링
- **모델 재학습**: 성능 저하 시 자동 재학습 트리거

## 7. 구현 로드맵

### 7.1. Phase 1: 기본 모델 개발 (1주)
- Baseline 모델 구현 (Linear Regression, Random Forest)
- 기본 특성 엔지니어링 파이프라인 구축
- Walk-Forward Validation 프레임워크 구현

### 7.2. Phase 2: 고급 모델 개발 (2주)
- XGBoost, LightGBM 모델 구현
- LSTM/GRU 딥러닝 모델 구현
- 하이퍼파라미터 튜닝 자동화

### 7.3. Phase 3: 통합 및 최적화 (1주)
- 모델 앙상블 구현
- 실시간 예측 파이프라인 구축
- 모니터링 및 알림 시스템 구축

---

**문서 작성자**: Gemini CLI  
**작성일**: 2024-12-23  
**버전**: 1.0.0
