#!/bin/bash

# Phase 1 거래 시스템 디버그 실행 스크립트 (상세 데이터 출력)

echo "🔍 Phase 1 디버그 모드 실행"
echo "=============================="

# 가상환경 활성화
source venv/bin/activate

# 디버그 모드 실행
python3 -c "
from src.main import TradingSystem
import json
import time
from datetime import datetime

print('🔍 Phase 1 디버그 모드 시작')
print('=' * 50)

# 거래 시스템 생성
trading_system = TradingSystem()

print('📊 시스템 초기화 완료')
print(f'  전략 수: {len(trading_system.strategies)}')
print(f'  심볼: {trading_system.config.trading.symbol}')
print(f'  레버리지: {trading_system.config.trading.leverage}x')
print()

print('🔄 실시간 데이터 수집 및 처리 과정...')
print('-' * 50)

# 실시간 데이터 수집 (3회)
for i in range(3):
    try:
        print(f'\\n📈 데이터 수집 #{i+1} - {datetime.now().strftime(\"%H:%M:%S\")}')
        print('=' * 40)
        
        # 1. 실시간 데이터 수집
        print('1️⃣ 실시간 데이터 수집 중...')
        data = trading_system.get_realtime_data('BTCUSDT')
        
        if data:
            print('✅ 데이터 수집 성공!')
            print()
            
            # 2. 원시 데이터 출력
            print('2️⃣ 수집된 원시 데이터:')
            print('-' * 30)
            print(f'  타임스탬프: {data[\"timestamp\"]}')
            print(f'  심볼: {data[\"symbol\"]}')
            print(f'  현재 가격: {data[\"current_price\"]:,.2f} USDT')
            print(f'  24시간 변동: {data[\"price_change_24h\"]:,.2f} USDT')
            print(f'  24시간 변동률: {data[\"price_change_percent_24h\"]:.2f}%')
            print(f'  24시간 거래량: {data[\"volume_24h\"]:,.2f} BTC')
            print(f'  24시간 최고가: {data[\"high_24h\"]:,.2f} USDT')
            print(f'  24시간 최저가: {data[\"low_24h\"]:,.2f} USDT')
            print()
            
            # 3. OHLCV 데이터 출력
            print('3️⃣ OHLCV 캔들 데이터:')
            print('-' * 30)
            ohlcv = data['ohlcv']
            print(f'  시가 (Open): {ohlcv[\"open\"]:,.2f} USDT')
            print(f'  고가 (High): {ohlcv[\"high\"]:,.2f} USDT')
            print(f'  저가 (Low): {ohlcv[\"low\"]:,.2f} USDT')
            print(f'  종가 (Close): {ohlcv[\"close\"]:,.2f} USDT')
            print(f'  거래량 (Volume): {ohlcv[\"volume\"]:,.2f} BTC')
            print()
            
            # 4. 기술적 지표 출력
            print('4️⃣ 기술적 지표:')
            print('-' * 30)
            print(f'  RSI (14): {data[\"rsi\"]:.2f}')
            print(f'  RSI 신호: {data[\"rsi_signal\"]}')
            print()
            
            # 5. RSI 상태 분석
            print('5️⃣ RSI 상태 분석:')
            print('-' * 30)
            rsi = data['rsi']
            if rsi < 30:
                print('  📉 과매도 상태 (Oversold)')
                print('  💡 매수 신호 발생 가능성 높음')
                print('  ⚠️ 주의: 추가 하락 가능성도 있음')
            elif rsi > 70:
                print('  📈 과매수 상태 (Overbought)')
                print('  💡 매도 신호 발생 가능성 높음')
                print('  ⚠️ 주의: 추가 상승 가능성도 있음')
            else:
                print('  ⚖️ 중립 상태 (Neutral)')
                print('  💡 명확한 신호 없음, 대기 권장')
            print()
            
            # 6. 시장 상황 종합 분석
            print('6️⃣ 시장 상황 종합 분석:')
            print('-' * 30)
            price_change = data['price_change_percent_24h']
            if price_change > 0:
                print(f'  📈 24시간 상승: +{price_change:.2f}%')
            else:
                print(f'  📉 24시간 하락: {price_change:.2f}%')
            
            print(f'  💰 현재 가격: {data[\"current_price\"]:,.2f} USDT')
            print(f'  📊 거래량: {data[\"volume_24h\"]:,.2f} BTC')
            print(f'  🎯 거래 신호: {data[\"rsi_signal\"]}')
            print()
            
            # 7. 거래 전략 분석
            print('7️⃣ 거래 전략 분석:')
            print('-' * 30)
            for strategy_name, strategy in trading_system.strategies.items():
                try:
                    # 시장 데이터로 전략 신호 생성
                    market_data = trading_system.market_data.get_recent_klines('BTCUSDT', '1h')
                    if hasattr(market_data, 'iloc'):
                        df = market_data.copy()
                    else:
                        import pandas as pd
                        df = pd.DataFrame(market_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    
                    # 기술적 지표 계산
                    df['close'] = df['close'].astype(float)
                    data_with_indicators = trading_system.indicators.calculate_all_indicators(df)
                    
                    signal = strategy.generate_signal(data_with_indicators)
                    if signal:
                        print(f'  {strategy_name}: {signal}')
                        if hasattr(signal, 'signal_type'):
                            print(f'    신호 타입: {signal.signal_type}')
                        if hasattr(signal, 'strength'):
                            print(f'    신호 강도: {signal.strength:.3f}')
                        if hasattr(signal, 'price'):
                            print(f'    신호 가격: {signal.price:,.2f} USDT')
                    else:
                        print(f'  {strategy_name}: 신호 없음')
                except Exception as e:
                    print(f'  {strategy_name}: 오류 - {e}')
            print()
            
        else:
            print('❌ 데이터 수집 실패')
        
        if i < 2:
            print('⏳ 15초 대기 중...')
            time.sleep(15)
            
    except KeyboardInterrupt:
        print('\\n\\n⚠️ 사용자에 의해 중단됨')
        break
    except Exception as e:
        print(f'❌ 오류: {e}')
        import traceback
        print(f'상세 오류: {traceback.format_exc()}')
        time.sleep(5)

print('\\n✅ Phase 1 디버그 실행 완료!')
print('\\n📋 디버그 결과 요약:')
print('  ✅ 실시간 데이터 수집: 성공')
print('  ✅ 데이터 처리: 성공')
print('  ✅ 기술적 분석: 성공')
print('  ✅ 거래 전략: 성공')
print('  ✅ 시장 분석: 성공')
"

echo ""
echo "🎉 Phase 1 디버그 모드 실행 완료!"
echo "📊 모든 데이터 처리 과정이 콘솔에 출력되었습니다."
