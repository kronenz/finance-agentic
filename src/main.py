"""
AI 기반 암호화폐 자동화 거래 시스템 - 메인 실행 파일

Phase 1: 최소 기능 자동화 거래 시스템
"""

import time
import signal
import sys
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

from core.config import get_config, reload_config
from core.logger import get_logger, log_system_event
from core.database import get_database
from data.market_data import get_market_data
from data.indicators import get_indicators
from strategies.supertrend import SupertrendStrategy
from strategies.rsi_mean_reversion import RSIMeanReversionStrategy


class TradingSystem:
    """메인 거래 시스템 클래스"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger("main")
        self.db = get_database()
        self.market_data = get_market_data()
        self.indicators = get_indicators()
        
        # 전략 초기화
        self.strategies = self._initialize_strategies()
        
        # 시스템 상태
        self.is_running = False
        self.last_update = None
        
        # 신호 처리기 설정
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("거래 시스템 초기화 완료")
    
    def _initialize_strategies(self) -> Dict[str, any]:
        """전략 초기화"""
        strategies = {}
        
        # 슈퍼트렌드 전략
        if self.config.strategies.supertrend.get('enabled', False):
            strategies['supertrend'] = SupertrendStrategy(
                self.config.strategies.supertrend
            )
            self.logger.info("슈퍼트렌드 전략 활성화")
        
        # RSI 평균회귀 전략
        if self.config.strategies.rsi_mean_reversion.get('enabled', False):
            strategies['rsi_mean_reversion'] = RSIMeanReversionStrategy(
                self.config.strategies.rsi_mean_reversion
            )
            self.logger.info("RSI 평균회귀 전략 활성화")
        
        return strategies
    
    def _signal_handler(self, signum, frame):
        """시그널 핸들러 (안전한 종료)"""
        self.logger.info(f"시그널 {signum} 수신, 시스템 종료 중...")
        self.stop()
    
    def start(self):
        """거래 시스템 시작"""
        try:
            self.logger.info("거래 시스템 시작")
            self.is_running = True
            
            # 시스템 이벤트 로깅
            self.db.log_system_event("info", "거래 시스템 시작")
            
            # 메인 루프
            while self.is_running:
                try:
                    self._main_loop()
                    time.sleep(self.config.data.update_interval_seconds)
                    
                except KeyboardInterrupt:
                    self.logger.info("사용자에 의한 중단")
                    break
                except Exception as e:
                    self.logger.error(f"메인 루프 오류: {e}")
                    self.db.log_system_event("error", f"메인 루프 오류: {e}")
                    time.sleep(10)  # 오류 후 잠시 대기
            
        except Exception as e:
            self.logger.error(f"시스템 시작 실패: {e}")
            raise
        finally:
            self.stop()
    
    def stop(self):
        """거래 시스템 중지"""
        self.logger.info("거래 시스템 중지")
        self.is_running = False
        self.db.log_system_event("info", "거래 시스템 중지")
    
    def _main_loop(self):
        """메인 실행 루프"""
        try:
            # 설정 재로드 (개발 중)
            if self.config.trading.testnet:
                self.config = reload_config()
                self.strategies = self._initialize_strategies()
            
            # 시장 데이터 수집
            symbol = self.config.trading.symbol
            timeframe = '1h'  # Phase 1에서는 1시간봉 사용
            
            data = self.market_data.get_recent_klines(symbol, timeframe, 200)
            
            if data.empty:
                self.logger.warning("시장 데이터가 비어있습니다")
                return
            
            # 기술적 지표 계산
            data_with_indicators = self.indicators.calculate_all_indicators(data)
            
            # 각 전략 실행
            for strategy_name, strategy in self.strategies.items():
                try:
                    self._execute_strategy(strategy_name, strategy, data_with_indicators)
                except Exception as e:
                    self.logger.error(f"전략 실행 실패 {strategy_name}: {e}")
            
            # 포지션 모니터링
            self._monitor_positions(data_with_indicators)
            
            # 시스템 상태 업데이트
            self.last_update = datetime.now()
            
        except Exception as e:
            self.logger.error(f"메인 루프 실행 실패: {e}")
            raise
    
    def _execute_strategy(self, strategy_name: str, strategy: any, data: pd.DataFrame):
        """개별 전략 실행"""
        try:
            # 신호 생성
            signal = strategy.generate_signal(data)
            
            if signal is None:
                return
            
            self.logger.info(f"전략 {strategy_name} 신호: {signal}")
            
            # 신호 처리
            if signal.signal_type in ['buy', 'sell']:
                self._process_signal(strategy_name, signal, data)
            
        except Exception as e:
            self.logger.error(f"전략 실행 실패 {strategy_name}: {e}")
    
    def _process_signal(self, strategy_name: str, signal: any, data: pd.DataFrame):
        """신호 처리 및 거래 실행"""
        try:
            symbol = self.config.trading.symbol
            current_price = signal.price
            
            # 포지션 크기 계산
            account_balance = 1000  # Phase 1에서는 고정값 사용
            position_size = strategy.calculate_position_size(
                account_balance=account_balance,
                risk_per_trade=self.config.trading.position_size_percent / 100,
                entry_price=current_price
            )
            
            # 거래 기록
            trade_data = {
                'strategy_name': strategy_name,
                'symbol': symbol,
                'side': signal.signal_type,
                'quantity': position_size / current_price,
                'price': current_price,
                'value': position_size,
                'leverage': self.config.trading.leverage,
                'metadata': {
                    'signal_strength': signal.strength,
                    'signal_metadata': signal.metadata
                }
            }
            
            # 데이터베이스에 기록
            trade_id = self.db.record_trade(trade_data)
            
            # 포지션 업데이트
            position = {
                'id': trade_id,
                'side': signal.signal_type,
                'entry_price': current_price,
                'quantity': position_size / current_price,
                'timestamp': signal.timestamp
            }
            strategy.update_position(position)
            
            # 시스템 이벤트 로깅
            self.db.log_system_event(
                "trade",
                f"거래 실행: {strategy_name} {signal.signal_type} {current_price:.2f}",
                trade_data
            )
            
            self.logger.info(f"거래 실행: {strategy_name} {signal.signal_type} "
                           f"가격={current_price:.2f}, 수량={position_size/current_price:.6f}")
            
        except Exception as e:
            self.logger.error(f"신호 처리 실패: {e}")
    
    def _monitor_positions(self, data: pd.DataFrame):
        """포지션 모니터링 및 청산"""
        try:
            for strategy_name, strategy in self.strategies.items():
                if not strategy.current_position:
                    continue
                
                current_price = data['close'].iloc[-1]
                entry_price = strategy.current_position['entry_price']
                
                # 청산 조건 확인
                should_exit, reason = strategy.should_exit_position(
                    current_price, entry_price, data
                )
                
                if should_exit:
                    self._close_position(strategy_name, strategy, current_price, reason)
                    
        except Exception as e:
            self.logger.error(f"포지션 모니터링 실패: {e}")
    
    def _close_position(self, strategy_name: str, strategy: any, 
                       current_price: float, reason: str):
        """포지션 청산"""
        try:
            position = strategy.current_position
            if not position:
                return
            
            # PnL 계산
            entry_price = position['entry_price']
            quantity = position['quantity']
            
            if position['side'] == 'buy':
                pnl = (current_price - entry_price) * quantity
            else:  # sell
                pnl = (entry_price - current_price) * quantity
            
            # 거래 기록 업데이트
            trade_id = position['id']
            update_data = {
                'status': 'closed',
                'close_timestamp': datetime.now(),
                'close_price': current_price,
                'close_pnl': pnl
            }
            
            self.db.update_trade(trade_id, update_data)
            
            # 포지션 초기화
            strategy.update_position(None)
            
            # 시스템 이벤트 로깅
            self.db.log_system_event(
                "trade",
                f"포지션 청산: {strategy_name} {reason} PnL={pnl:.2f}",
                {
                    'strategy_name': strategy_name,
                    'reason': reason,
                    'pnl': pnl,
                    'entry_price': entry_price,
                    'close_price': current_price
                }
            )
            
            self.logger.info(f"포지션 청산: {strategy_name} {reason} "
                           f"PnL={pnl:.2f} ({entry_price:.2f} -> {current_price:.2f})")
            
        except Exception as e:
            self.logger.error(f"포지션 청산 실패: {e}")
    
    def get_system_status(self) -> Dict[str, any]:
        """시스템 상태 조회"""
        return {
            'is_running': self.is_running,
            'last_update': self.last_update,
            'strategies': {
                name: strategy.get_strategy_info() 
                for name, strategy in self.strategies.items()
            },
            'config': {
                'symbol': self.config.trading.symbol,
                'leverage': self.config.trading.leverage,
                'testnet': self.config.trading.testnet
            }
        }


def main():
    """메인 함수"""
    try:
        # 거래 시스템 생성 및 시작
        trading_system = TradingSystem()
        trading_system.start()
        
    except KeyboardInterrupt:
        print("\n사용자에 의한 중단")
    except Exception as e:
        print(f"시스템 오류: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
