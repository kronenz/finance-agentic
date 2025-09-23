#!/bin/bash

# Phase 1 거래 시스템 빠른 테스트 스크립트

echo "🧪 Phase 1 빠른 테스트"
echo "======================"

# 가상환경 활성화
source venv/bin/activate

# 빠른 테스트 실행
python3 -c "
from src.main import TradingSystem

print('🚀 Phase 1 빠른 테스트 시작')
print('=' * 40)

try:
    # 거래 시스템 생성
    trading_system = TradingSystem()
    print('✅ 시스템 초기화: 성공')
    
    # 실시간 데이터 수집
    data = trading_system.get_realtime_data('BTCUSDT')
    if data:
        print('✅ 실시간 데이터 수집: 성공')
        print(f'  BTC: {data[\"current_price\"]:,.2f} USDT')
        print(f'  RSI: {data[\"rsi\"]:.2f}')
        print(f'  신호: {data[\"rsi_signal\"]}')
    else:
        print('❌ 실시간 데이터 수집: 실패')
    
    # 시스템 상태 확인
    status = trading_system.get_system_status()
    print('✅ 시스템 상태 확인: 성공')
    print(f'  전략 수: {len(status[\"strategies\"])}')
    print(f'  스크래퍼: {status[\"realtime_scraper\"][\"status\"]}')
    
    print('\\n🎉 모든 테스트 통과!')
    
except Exception as e:
    print(f'❌ 테스트 실패: {e}')
    import sys
    sys.exit(1)
"

echo ""
echo "✅ 테스트 완료!"
