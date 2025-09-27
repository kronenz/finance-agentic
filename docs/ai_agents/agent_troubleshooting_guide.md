# AI 에이전트 문제 해결 가이드

## 개요

AI 에이전트 시스템에서 발생할 수 있는 일반적인 문제들과 해결 방법을 제공합니다.

## 일반적인 문제 유형

### 1. 에이전트 연결 문제

#### 증상
- 에이전트가 응답하지 않음
- WebSocket 연결 끊김
- 메시지 전송 실패

#### 원인
- 네트워크 연결 문제
- 에이전트 프로세스 종료
- 메모리 부족
- 포트 충돌

#### 해결 방법
```bash
# 1. 에이전트 상태 확인
curl http://localhost:8000/api/v1/agents/status

# 2. 프로세스 확인
ps aux | grep python | grep agent

# 3. 포트 사용 확인
netstat -tulpn | grep :8000

# 4. 로그 확인
tail -f logs/agent.log

# 5. 에이전트 재시작
systemctl restart ai-trading-agent
```

### 2. 성능 저하 문제

#### 증상
- 응답 시간 증가
- 처리량 감소
- 메모리 사용량 증가
- CPU 사용률 증가

#### 원인
- 데이터베이스 연결 풀 고갈
- 메모리 누수
- 비효율적인 알고리즘
- 리소스 경합

#### 해결 방법
```python
# 1. 성능 프로파일링
import cProfile
import pstats

def profile_agent():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # 에이전트 작업 실행
    agent.process_market_data()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)

# 2. 메모리 사용량 모니터링
import tracemalloc

def monitor_memory():
    tracemalloc.start()
    
    # 에이전트 작업 실행
    agent.process_market_data()
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage: {current / 1024 / 1024:.2f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.2f} MB")

# 3. 데이터베이스 연결 최적화
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)
```

### 3. AI 모델 성능 문제

#### 증상
- 예측 정확도 감소
- 신뢰도 점수 하락
- 모델 학습 실패
- 예측 시간 증가

#### 원인
- 데이터 품질 저하
- 모델 오버피팅
- 하이퍼파라미터 부적절
- 학습 데이터 부족

#### 해결 방법
```python
# 1. 데이터 품질 검사
def check_data_quality(data):
    # 결측값 확인
    missing_values = data.isnull().sum()
    print(f"Missing values: {missing_values}")
    
    # 이상값 확인
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    outliers = data[(data < Q1 - 1.5 * IQR) | (data > Q3 + 1.5 * IQR)]
    print(f"Outliers: {len(outliers)}")
    
    # 데이터 분포 확인
    print(data.describe())

# 2. 모델 성능 평가
from sklearn.metrics import accuracy_score, precision_score, recall_score

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall = recall_score(y_test, y_pred, average='weighted')
    
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    
    return accuracy, precision, recall

# 3. 하이퍼파라미터 튜닝
from sklearn.model_selection import GridSearchCV

def tune_hyperparameters(model, X_train, y_train):
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [10, 20, 30],
        'learning_rate': [0.01, 0.1, 0.2]
    }
    
    grid_search = GridSearchCV(
        model, param_grid, cv=5, scoring='accuracy'
    )
    grid_search.fit(X_train, y_train)
    
    print(f"Best parameters: {grid_search.best_params_}")
    print(f"Best score: {grid_search.best_score_}")
    
    return grid_search.best_estimator_
```

### 4. 데이터베이스 연결 문제

#### 증상
- 데이터베이스 연결 실패
- 쿼리 타임아웃
- 트랜잭션 롤백
- 연결 풀 고갈

#### 원인
- 데이터베이스 서버 다운
- 네트워크 문제
- 연결 수 제한 초과
- 쿼리 성능 문제

#### 해결 방법
```python
# 1. 연결 상태 확인
def check_database_connection():
    try:
        from sqlalchemy import create_engine
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("Database connection successful")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

# 2. 연결 풀 모니터링
def monitor_connection_pool(engine):
    pool = engine.pool
    print(f"Pool size: {pool.size()}")
    print(f"Checked out connections: {pool.checkedout()}")
    print(f"Overflow: {pool.overflow()}")
    print(f"Invalid connections: {pool.invalid()})

# 3. 쿼리 최적화
def optimize_query():
    # 인덱스 사용 확인
    query = """
    EXPLAIN ANALYZE 
    SELECT * FROM trading_signals 
    WHERE symbol = 'BTCUSDT' 
    AND created_at > NOW() - INTERVAL '1 day'
    """
    
    # 느린 쿼리 로그 확인
    # PostgreSQL 설정에서 log_min_duration_statement = 1000
```

### 5. 메모리 누수 문제

#### 증상
- 메모리 사용량 지속적 증가
- 시스템 성능 저하
- OutOfMemoryError 발생
- 가비지 컬렉션 빈도 증가

#### 원인
- 순환 참조
- 이벤트 리스너 미해제
- 캐시 크기 무제한 증가
- 대용량 객체 누적

#### 해결 방법
```python
# 1. 메모리 사용량 모니터링
import psutil
import gc

def monitor_memory():
    process = psutil.Process()
    memory_info = process.memory_info()
    print(f"RSS: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"VMS: {memory_info.vms / 1024 / 1024:.2f} MB")
    
    # 가비지 컬렉션 강제 실행
    collected = gc.collect()
    print(f"Garbage collected: {collected} objects")

# 2. 순환 참조 해결
import weakref

class Agent:
    def __init__(self):
        self.callbacks = []
    
    def add_callback(self, callback):
        # weakref 사용으로 순환 참조 방지
        self.callbacks.append(weakref.ref(callback))
    
    def cleanup(self):
        # 콜백 정리
        self.callbacks.clear()

# 3. 캐시 크기 제한
from functools import lru_cache
import threading

class LimitedCache:
    def __init__(self, max_size=1000):
        self.cache = {}
        self.max_size = max_size
        self.lock = threading.Lock()
    
    def get(self, key):
        with self.lock:
            return self.cache.get(key)
    
    def set(self, key, value):
        with self.lock:
            if len(self.cache) >= self.max_size:
                # 가장 오래된 항목 제거
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            self.cache[key] = value
```

## 디버깅 도구

### 1. 로깅 설정
```python
import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/agent.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # 특정 모듈 로그 레벨 설정
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
```

### 2. 디버거 설정
```python
import pdb
import traceback

def debug_agent():
    try:
        # 에이전트 작업 실행
        agent.process_market_data()
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        pdb.set_trace()  # 디버거 시작
```

### 3. 모니터링 도구
```python
# Prometheus 메트릭 수집
from prometheus_client import Counter, Histogram, Gauge

# 에러 카운터
error_counter = Counter('agent_errors_total', 'Total agent errors', ['agent_id', 'error_type'])

# 응답 시간 히스토그램
response_time = Histogram('agent_response_time_seconds', 'Agent response time', ['agent_id'])

# 메모리 사용량 게이지
memory_usage = Gauge('agent_memory_usage_bytes', 'Agent memory usage', ['agent_id'])
```

## 예방 조치

### 1. 정기적인 모니터링
- **시스템 리소스**: CPU, 메모리, 디스크 사용량
- **애플리케이션 성능**: 응답 시간, 처리량, 에러율
- **데이터베이스**: 연결 수, 쿼리 성능, 인덱스 사용률
- **네트워크**: 대역폭, 지연시간, 패킷 손실

### 2. 자동화된 테스트
- **단위 테스트**: 개별 함수 및 메서드 테스트
- **통합 테스트**: 에이전트 간 상호작용 테스트
- **성능 테스트**: 부하 및 스트레스 테스트
- **보안 테스트**: 취약점 스캔 및 침투 테스트

### 3. 백업 및 복구
- **데이터 백업**: 정기적인 데이터베이스 백업
- **설정 백업**: 에이전트 설정 및 구성 백업
- **코드 백업**: 버전 관리 시스템 활용
- **재해 복구**: 장애 시 복구 절차 수립

### 4. 문서화
- **운영 매뉴얼**: 시스템 운영 절차 문서화
- **문제 해결 가이드**: 일반적인 문제 해결 방법
- **변경 이력**: 시스템 변경 사항 기록
- **성능 기준**: 성능 목표 및 임계값 정의

