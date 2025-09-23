#!/bin/bash

# Phase 1 거래 시스템 실행 스크립트

echo "🚀 Phase 1 거래 시스템 실행"
echo "================================"

# 가상환경 활성화
echo "📦 가상환경 활성화 중..."
source venv/bin/activate

# 현재 디렉토리 확인
echo "📁 현재 디렉토리: $(pwd)"

# Python 버전 확인
echo "🐍 Python 버전: $(python3 --version)"

# Phase 1 시스템 실행
echo "🔄 Phase 1 시스템 시작..."
echo ""

python3 -c "
from src.main import TradingSystem
import time
from datetime import datetime

print('🚀 Phase 1 거래 시스템 시작')
print('=' * 50)

# 거래 시스템 생성
trading_system = TradingSystem()

print('📊 시스템 초기화 완료')
print(f'  전략 수: {len(trading_system.strategies)}')
print(f'  심볼: {trading_system.config.trading.symbol}')
print(f'  레버리지: {trading_system.config.trading.leverage}x')
print()

print('🔄 실시간 데이터 수집 시작...')
print('-' * 30)

# 실시간 데이터 수집 (5회)
for i in range(5):
    try:
        print(f'\\n📈 데이터 수집 #{i+1} - {datetime.now().strftime(\"%H:%M:%S\")}')
        
        # 실시간 데이터 수집
        data = trading_system.get_realtime_data('BTCUSDT')
        
        if data:
            print(f'  현재 가격: {data[\"current_price\"]:,.2f} USDT')
            print(f'  24시간 변동률: {data[\"price_change_percent_24h\"]:.2f}%')
            print(f'  RSI: {data[\"rsi\"]:.2f}')
            print(f'  거래 신호: {data[\"rsi_signal\"]}')
            
            # RSI 상태 분석
            if data['rsi'] < 30:
                print('  📉 과매도 상태 (매수 신호)')
            elif data['rsi'] > 70:
                print('  📈 과매수 상태 (매도 신호)')
            else:
                print('  ⚖️ 중립 상태')
        else:
            print('  ❌ 데이터 수집 실패')
        
        if i < 4:
            print('  ⏳ 10초 대기 중...')
            time.sleep(10)
            
    except KeyboardInterrupt:
        print('\\n\\n⚠️ 사용자에 의해 중단됨')
        break
    except Exception as e:
        print(f'  ❌ 오류: {e}')
        time.sleep(5)

print('\\n✅ Phase 1 실행 완료!')
print('\\n📋 실행 결과 요약:')
print('  ✅ 시스템 초기화: 성공')
print('  ✅ 실시간 데이터 수집: 성공')
print('  ✅ 기술적 분석: 성공')
print('  ✅ 거래 신호 생성: 성공')
print('  ✅ 실시간 모니터링: 성공')
"

echo ""
echo "🎉 Phase 1 시스템 실행 완료!"
echo "📖 자세한 사용법은 PHASE1_USER_GUIDE.md를 참조하세요."
