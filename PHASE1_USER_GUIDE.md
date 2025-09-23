# Phase 1 거래 시스템 사용자 가이드

## 🚀 Phase 1 시스템 직접 실행하기

### 1. 환경 설정

#### 1.1 가상환경 활성화
```bash
cd /root/develop/finance
source venv/bin/activate
```

#### 1.2 의존성 확인
```bash
pip list | grep -E "(pandas|numpy|ccxt|ta-lib|rich|schedule)"
```

### 2. Phase 1 시스템 실행 방법

#### 2.1 빠른 테스트 (권장)
```bash
cd /root/develop/finance
./test_phase1.sh
```

#### 2.2 디버그 모드 (상세 데이터 출력)
```bash
cd /root/develop/finance
./debug_phase1.sh
```

#### 2.3 실시간 모니터링
```bash
cd /root/develop/finance
./monitor_phase1.sh
```

#### 2.4 기본 실행
```bash
cd /root/develop/finance
source venv/bin/activate
python3 -c "
from src.main import TradingSystem
import time

# 거래 시스템 생성
trading_system = TradingSystem()

print('🚀 Phase 1 거래 시스템 시작')
print('=' * 40)

# 실시간 데이터 수집 (5회)
for i in range(5):
    data = trading_system.get_realtime_data('BTCUSDT')
    if data:
        print(f'#{i+1} BTC: {data[\"current_price\"]:,.2f} USDT, RSI: {data[\"rsi\"]:.2f}, 신호: {data[\"rsi_signal\"]}')
    time.sleep(10)

print('✅ 실행 완료!')
"
```

#### 2.2 연속 스크래핑 실행
```bash
cd /root/develop/finance
source venv/bin/activate
python3 -c "
from src.main import TradingSystem

# 거래 시스템 생성
trading_system = TradingSystem()

print('🔄 연속 실시간 스크래핑 시작')
print('=' * 40)

# 연속 스크래핑 (10초 간격, 10회)
scraped_data = trading_system.start_realtime_scraping('BTCUSDT', interval=10, max_iterations=10)

print(f'✅ 수집 완료: {len(scraped_data)}개 데이터')
"
```

#### 2.3 메인 루프 시뮬레이션
```bash
cd /root/develop/finance
source venv/bin/activate
python3 -c "
from src.main import TradingSystem
import time

# 거래 시스템 생성
trading_system = TradingSystem()

print('🔄 메인 루프 시뮬레이션')
print('=' * 40)

# 메인 루프 시뮬레이션 (3회)
for i in range(3):
    print(f'\\n🔄 루프 #{i+1}')
    
    # 시장 데이터 수집
    data = trading_system.market_data.get_recent_klines('BTCUSDT', '1h', 200)
    if not data.empty:
        # 기술적 지표 계산
        data_with_indicators = trading_system.indicators.calculate_all_indicators(data)
        current_price = data_with_indicators['close'].iloc[-1]
        
        print(f'  현재 가격: {current_price:,.2f} USDT')
        
        # RSI 확인
        if 'rsi' in data_with_indicators.columns:
            rsi = data_with_indicators['rsi'].iloc[-1]
            print(f'  RSI: {rsi:.2f}')
            
            if rsi < 30:
                print('  📉 과매도 상태 (매수 신호)')
            elif rsi > 70:
                print('  📈 과매수 상태 (매도 신호)')
            else:
                print('  ⚖️ 중립 상태')
        
        # 전략 실행
        for strategy_name, strategy in trading_system.strategies.items():
            try:
                signal = strategy.generate_signal(data_with_indicators)
                if signal:
                    print(f'  {strategy_name}: {signal}')
                else:
                    print(f'  {strategy_name}: 신호 없음')
            except Exception as e:
                print(f'  {strategy_name}: 오류 - {e}')
    
    if i < 2:
        time.sleep(15)

print('\\n✅ 시뮬레이션 완료!')
"
```

### 3. 고급 사용법

#### 3.1 시스템 상태 확인
```bash
cd /root/develop/finance
source venv/bin/activate
python3 -c "
from src.main import TradingSystem

trading_system = TradingSystem()
status = trading_system.get_system_status()

print('📊 시스템 상태')
print('=' * 30)
print(f'실행 중: {status[\"is_running\"]}')
print(f'전략 수: {len(status[\"strategies\"])}')
print(f'실시간 스크래퍼: {status[\"realtime_scraper\"][\"status\"]}')
print(f'심볼: {status[\"config\"][\"symbol\"]}')
print(f'레버리지: {status[\"config\"][\"leverage\"]}x')
"
```

#### 3.2 실시간 데이터 분석
```bash
cd /root/develop/finance
source venv/bin/activate
python3 -c "
from src.main import TradingSystem

trading_system = TradingSystem()

# 실시간 데이터 수집
data = trading_system.get_realtime_data('BTCUSDT')

if data:
    print('📊 실시간 시장 분석')
    print('=' * 30)
    print(f'시간: {data[\"timestamp\"]}')
    print(f'현재 가격: {data[\"current_price\"]:,.2f} USDT')
    print(f'24시간 변동률: {data[\"price_change_percent_24h\"]:.2f}%')
    print(f'24시간 거래량: {data[\"volume_24h\"]:,.2f} BTC')
    print(f'24시간 최고가: {data[\"high_24h\"]:,.2f} USDT')
    print(f'24시간 최저가: {data[\"low_24h\"]:,.2f} USDT')
    print(f'RSI: {data[\"rsi\"]:.2f}')
    print(f'거래 신호: {data[\"rsi_signal\"]}')
    
    # OHLCV 데이터
    ohlcv = data['ohlcv']
    print(f'\\n📈 최근 1시간봉:')
    print(f'  시가: {ohlcv[\"open\"]:,.2f} USDT')
    print(f'  고가: {ohlcv[\"high\"]:,.2f} USDT')
    print(f'  저가: {ohlcv[\"low\"]:,.2f} USDT')
    print(f'  종가: {ohlcv[\"close\"]:,.2f} USDT')
    print(f'  거래량: {ohlcv[\"volume\"]:,.2f} BTC')
"
```

### 4. 문제 해결

#### 4.1 일반적인 오류
- **ModuleNotFoundError**: 가상환경이 활성화되지 않음
  ```bash
  source venv/bin/activate
  ```

- **API 연결 오류**: 인터넷 연결 확인
  ```bash
  ping binance.com
  ```

- **데이터베이스 오류**: SQLite 파일 권한 확인
  ```bash
  ls -la data/
  ```

#### 4.2 로그 확인
```bash
tail -f logs/trading.log
```

### 5. 설정 변경

#### 5.1 거래 심볼 변경
`config/config.yaml` 파일에서 `trading.symbol` 수정

#### 5.2 전략 설정 변경
`config/config.yaml` 파일에서 `strategies` 섹션 수정

#### 5.3 리스크 관리 설정
`config/config.yaml` 파일에서 `risk_management` 섹션 수정

### 6. 실행 예시

#### 6.1 빠른 테스트
```bash
cd /root/develop/finance && source venv/bin/activate && python3 -c "
from src.main import TradingSystem
trading_system = TradingSystem()
data = trading_system.get_realtime_data('BTCUSDT')
print(f'BTC: {data[\"current_price\"]:,.2f} USDT, RSI: {data[\"rsi\"]:.2f}, 신호: {data[\"rsi_signal\"]}')
"
```

#### 6.2 연속 모니터링
```bash
cd /root/develop/finance && source venv/bin/activate && python3 -c "
from src.main import TradingSystem
import time

trading_system = TradingSystem()
print('🔄 실시간 모니터링 시작 (Ctrl+C로 중단)')

try:
    while True:
        data = trading_system.get_realtime_data('BTCUSDT')
        if data:
            print(f'[{time.strftime(\"%H:%M:%S\")}] BTC: {data[\"current_price\"]:,.2f} USDT, RSI: {data[\"rsi\"]:.2f}, 신호: {data[\"rsi_signal\"]}')
        time.sleep(10)
except KeyboardInterrupt:
    print('\\n✅ 모니터링 종료')
"
```

## 🎯 주요 기능

- ✅ **실시간 데이터 수집**: 바이낸스 API를 통한 실시간 비트코인 데이터
- ✅ **기술적 분석**: RSI, 이동평균선 등 고급 기술적 지표
- ✅ **거래 전략**: 슈퍼트렌드, RSI 평균회귀 전략
- ✅ **리스크 관리**: 포지션 크기, 손절매, 연속 손실 제한
- ✅ **실시간 모니터링**: 지속적인 시장 분석 및 신호 생성

## 📞 지원

문제가 발생하면 로그 파일을 확인하거나 시스템 상태를 점검해보세요.

```bash
# 시스템 상태 확인
python3 -c "from src.main import TradingSystem; print(TradingSystem().get_system_status())"

# 로그 확인
tail -f logs/trading.log
```
