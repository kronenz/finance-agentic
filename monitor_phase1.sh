#!/bin/bash

# Phase 1 실시간 모니터링 스크립트 (간단한 출력)

echo "📊 Phase 1 실시간 모니터링 시작"
echo "================================"
echo "Ctrl+C로 중단 가능"
echo ""

# 가상환경 활성화
source venv/bin/activate

# 실시간 모니터링 실행
python3 -c "
from src.main import TradingSystem
import time
from datetime import datetime

print('🔄 실시간 모니터링 시작...')
print('=' * 50)

# 거래 시스템 생성
trading_system = TradingSystem()

try:
    count = 0
    while True:
        count += 1
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # 실시간 데이터 수집
        data = trading_system.get_realtime_data('BTCUSDT')
        
        if data:
            # 간단한 출력
            print(f'[{timestamp}] #{count:03d} | BTC: {data[\"current_price\"]:,.2f} USDT | RSI: {data[\"rsi\"]:.2f} | 신호: {data[\"rsi_signal\"]} | 변동: {data[\"price_change_percent_24h\"]:+.2f}%')
            
            # RSI 상태에 따른 색상 표시
            rsi = data['rsi']
            if rsi < 30:
                print(f'    📉 과매도 상태 - 매수 신호 강함')
            elif rsi > 70:
                print(f'    📈 과매수 상태 - 매도 신호 강함')
            else:
                print(f'    ⚖️ 중립 상태 - 대기 권장')
        else:
            print(f'[{timestamp}] #{count:03d} | ❌ 데이터 수집 실패')
        
        time.sleep(10)  # 10초 간격
        
except KeyboardInterrupt:
    print('\\n\\n✅ 모니터링 종료')
except Exception as e:
    print(f'\\n❌ 오류: {e}')
"

echo ""
echo "🎉 모니터링 완료!"
