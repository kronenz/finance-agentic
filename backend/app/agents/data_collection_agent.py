# 데이터 수집 에이전트
import asyncio
import ccxt
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime, timedelta
import structlog

from .base_agent import BaseAgent

logger = structlog.get_logger()

class DataCollectionAgent(BaseAgent):
    """시장 데이터 수집 에이전트"""
    
    def __init__(self, agent_id: str = "data_collection", redis_url: str = "redis://localhost:6379"):
        super().__init__(agent_id, "DataCollectionAgent", redis_url)
        self.exchanges = {}
        self.data_sources = {
            'binance': 'binance',
            'coinbase': 'coinbasepro',
            'kraken': 'kraken'
        }
        
    async def initialize(self):
        """에이전트 초기화"""
        # 거래소 연결 설정
        for name, exchange_id in self.data_sources.items():
            try:
                exchange_class = getattr(ccxt, exchange_id)
                self.exchanges[name] = exchange_class({
                    'apiKey': '',  # 실제 사용 시 환경변수에서 로드
                    'secret': '',
                    'sandbox': True,  # 테스트 환경
                    'rateLimit': 1200,
                    'enableRateLimit': True,
                })
                logger.info(f"Exchange {name} initialized")
            except Exception as e:
                logger.error(f"Failed to initialize exchange {name}: {e}")
                
        # 메시지 핸들러 등록
        self.register_handler("COLLECT_MARKET_DATA", self.handle_collect_market_data)
        self.register_handler("COLLECT_HISTORICAL_DATA", self.handle_collect_historical_data)
        self.register_handler("GET_MARKET_STATUS", self.handle_get_market_status)
        
    async def cleanup(self):
        """에이전트 정리"""
        # 거래소 연결 종료
        for exchange in self.exchanges.values():
            if hasattr(exchange, 'close'):
                await exchange.close()
                
    async def handle_collect_market_data(self, message: Dict[str, Any]):
        """실시간 시장 데이터 수집 처리"""
        try:
            payload = message["payload"]
            symbol = payload.get("symbol", "BTC/USDT")
            exchange_name = payload.get("exchange", "binance")
            timeframe = payload.get("timeframe", "1h")
            
            logger.info(f"Collecting market data", 
                       symbol=symbol, 
                       exchange=exchange_name,
                       timeframe=timeframe)
            
            # 데이터 수집
            data = await self.collect_ohlcv_data(symbol, exchange_name, timeframe)
            
            # 분석 에이전트에게 데이터 전송
            await self.send_message(
                recipient="data_analysis",
                task_name="NEW_MARKET_DATA",
                payload={
                    "symbol": symbol,
                    "exchange": exchange_name,
                    "timeframe": timeframe,
                    "data": data.to_dict('records'),
                    "timestamp": datetime.utcnow().isoformat()
                },
                correlation_id=message["correlation_id"]
            )
            
            logger.info(f"Market data collected and sent", 
                       symbol=symbol,
                       data_points=len(data))
                       
        except Exception as e:
            logger.error(f"Error collecting market data: {e}")
            await self._send_error_response(message, str(e))
            
    async def handle_collect_historical_data(self, message: Dict[str, Any]):
        """과거 데이터 수집 처리"""
        try:
            payload = message["payload"]
            symbol = payload.get("symbol", "BTC/USDT")
            exchange_name = payload.get("exchange", "binance")
            timeframe = payload.get("timeframe", "1h")
            start_date = payload.get("start_date")
            end_date = payload.get("end_date")
            
            logger.info(f"Collecting historical data", 
                       symbol=symbol, 
                       exchange=exchange_name,
                       start_date=start_date,
                       end_date=end_date)
            
            # 과거 데이터 수집
            data = await self.collect_historical_data(symbol, exchange_name, 
                                                    timeframe, start_date, end_date)
            
            # 데이터 저장 및 분석 에이전트에게 전송
            await self.send_message(
                recipient="data_analysis",
                task_name="HISTORICAL_DATA_READY",
                payload={
                    "symbol": symbol,
                    "exchange": exchange_name,
                    "timeframe": timeframe,
                    "data_path": f"/data/historical/{symbol.replace('/', '_')}_{timeframe}.csv",
                    "data_points": len(data),
                    "start_date": start_date,
                    "end_date": end_date
                },
                correlation_id=message["correlation_id"]
            )
            
            logger.info(f"Historical data collected", 
                       symbol=symbol,
                       data_points=len(data))
                       
        except Exception as e:
            logger.error(f"Error collecting historical data: {e}")
            await self._send_error_response(message, str(e))
            
    async def handle_get_market_status(self, message: Dict[str, Any]):
        """시장 상태 조회 처리"""
        try:
            payload = message["payload"]
            exchange_name = payload.get("exchange", "binance")
            
            status = await self.get_market_status(exchange_name)
            
            await self.send_message(
                recipient=message["sender_agent_id"],
                task_name="MARKET_STATUS_RESPONSE",
                payload=status,
                correlation_id=message["correlation_id"]
            )
            
        except Exception as e:
            logger.error(f"Error getting market status: {e}")
            await self._send_error_response(message, str(e))
            
    async def collect_ohlcv_data(self, symbol: str, exchange_name: str, timeframe: str) -> pd.DataFrame:
        """OHLCV 데이터 수집"""
        try:
            exchange = self.exchanges.get(exchange_name)
            if not exchange:
                raise ValueError(f"Exchange {exchange_name} not available")
                
            # 최근 100개 캔들 데이터 수집
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
            
            # DataFrame으로 변환
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['symbol'] = symbol
            df['exchange'] = exchange_name
            df['timeframe'] = timeframe
            
            return df
            
        except Exception as e:
            logger.error(f"Error collecting OHLCV data: {e}")
            raise
            
    async def collect_historical_data(self, symbol: str, exchange_name: str, 
                                    timeframe: str, start_date: str, end_date: str) -> pd.DataFrame:
        """과거 데이터 수집"""
        try:
            exchange = self.exchanges.get(exchange_name)
            if not exchange:
                raise ValueError(f"Exchange {exchange_name} not available")
                
            # 날짜 변환
            start_ts = int(pd.to_datetime(start_date).timestamp() * 1000)
            end_ts = int(pd.to_datetime(end_date).timestamp() * 1000)
            
            all_data = []
            current_ts = start_ts
            
            while current_ts < end_ts:
                try:
                    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=current_ts, limit=1000)
                    if not ohlcv:
                        break
                        
                    all_data.extend(ohlcv)
                    current_ts = ohlcv[-1][0] + 1
                    
                    # Rate limiting
                    await asyncio.sleep(exchange.rateLimit / 1000)
                    
                except Exception as e:
                    logger.warning(f"Error fetching batch: {e}")
                    break
                    
            # DataFrame으로 변환
            df = pd.DataFrame(all_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['symbol'] = symbol
            df['exchange'] = exchange_name
            df['timeframe'] = timeframe
            
            # 중복 제거 및 정렬
            df = df.drop_duplicates(subset=['timestamp']).sort_values('timestamp')
            
            return df
            
        except Exception as e:
            logger.error(f"Error collecting historical data: {e}")
            raise
            
    async def get_market_status(self, exchange_name: str) -> Dict[str, Any]:
        """시장 상태 조회"""
        try:
            exchange = self.exchanges.get(exchange_name)
            if not exchange:
                raise ValueError(f"Exchange {exchange_name} not available")
                
            # 시장 상태 조회
            status = exchange.fetch_status()
            
            return {
                "exchange": exchange_name,
                "status": status.get("status", "unknown"),
                "updated": status.get("updated", None),
                "eta": status.get("eta", None)
            }
            
        except Exception as e:
            logger.error(f"Error getting market status: {e}")
            raise
