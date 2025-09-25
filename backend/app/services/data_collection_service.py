# 데이터 수집 서비스
import asyncio
import ccxt
import pandas as pd
import redis
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import structlog
from dataclasses import dataclass

from app.services.base_service import BaseService

logger = structlog.get_logger()

@dataclass
class MarketData:
    """시장 데이터 구조체"""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    exchange: str
    timeframe: str

class DataCollectionService(BaseService):
    """실시간 시장 데이터 수집 서비스"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        super().__init__(redis_url)
        self.exchanges = {}
        self.collection_tasks = {}
        
        # 지원하는 거래소 설정
        self.supported_exchanges = {
            'binance': {
                'class': ccxt.binance,
                'rate_limit': 1200,
                'sandbox': True
            },
            'coinbase': {
                'class': ccxt.coinbasepro,
                'rate_limit': 1000,
                'sandbox': True
            },
            'kraken': {
                'class': ccxt.kraken,
                'rate_limit': 3000,
                'sandbox': True
            }
        }
        
    async def initialize(self):
        """서비스 초기화"""
        await super().initialize()
        try:
            # 거래소 연결 설정
            for name, config in self.supported_exchanges.items():
                exchange_class = config['class']
                self.exchanges[name] = exchange_class({
                    'apiKey': '',  # 실제 사용 시 환경변수에서 로드
                    'secret': '',
                    'sandbox': config['sandbox'],
                    'rateLimit': config['rate_limit'],
                    'enableRateLimit': True,
                })
                logger.info(f"Exchange {name} initialized", 
                           rate_limit=config['rate_limit'])
            
            logger.info("Data collection service exchanges initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize data collection service exchanges: {e}")
            raise
            
    async def start_collection(self, symbols: List[str], exchanges: List[str] = None):
        """데이터 수집 시작"""
        if exchanges is None:
            exchanges = list(self.exchanges.keys())
            
        self.is_running = True
        
        # 각 거래소별로 수집 작업 시작
        for exchange_name in exchanges:
            if exchange_name not in self.exchanges:
                logger.warning(f"Exchange {exchange_name} not supported")
                continue
                
            task = asyncio.create_task(
                self._collect_exchange_data(exchange_name, symbols)
            )
            self.collection_tasks[exchange_name] = task
            
        logger.info(f"Data collection started for {len(exchanges)} exchanges", 
                   exchanges=exchanges, symbols=symbols)
        
    async def stop_collection(self):
        """데이터 수집 중지"""
        self.is_running = False
        
        # 모든 수집 작업 중지
        for task in self.collection_tasks.values():
            task.cancel()
            
        # 작업 완료 대기
        await asyncio.gather(*self.collection_tasks.values(), return_exceptions=True)
        self.collection_tasks.clear()
        
        logger.info("Data collection stopped")
        
    async def _collect_exchange_data(self, exchange_name: str, symbols: List[str]):
        """특정 거래소의 데이터 수집"""
        exchange = self.exchanges[exchange_name]
        
        try:
            while self.is_running:
                for symbol in symbols:
                    try:
                        # OHLCV 데이터 수집
                        ohlcv_data = await self._fetch_ohlcv_data(exchange, symbol)
                        
                        if ohlcv_data:
                            # 데이터 처리 및 저장
                            await self._process_and_store_data(exchange_name, symbol, ohlcv_data)
                            
                    except Exception as e:
                        logger.error(f"Error collecting data for {symbol} on {exchange_name}: {e}")
                        
                # Rate limiting
                await asyncio.sleep(exchange.rateLimit / 1000)
                
        except asyncio.CancelledError:
            logger.info(f"Data collection cancelled for {exchange_name}")
        except Exception as e:
            logger.error(f"Data collection error for {exchange_name}: {e}")
            
    async def _fetch_ohlcv_data(self, exchange, symbol: str) -> Optional[List]:
        """OHLCV 데이터 수집"""
        try:
            # 최근 100개 캔들 데이터 수집
            ohlcv = exchange.fetch_ohlcv(symbol, '1m', limit=100)
            return ohlcv
        except Exception as e:
            logger.error(f"Failed to fetch OHLCV data for {symbol}: {e}")
            return None
            
    async def _process_and_store_data(self, exchange_name: str, symbol: str, ohlcv_data: List):
        """데이터 처리 및 저장"""
        try:
            # DataFrame으로 변환
            df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['symbol'] = symbol
            df['exchange'] = exchange_name
            df['timeframe'] = '1m'
            
            # Redis Streams에 데이터 전송
            await self._send_to_redis_stream(df)
            
            # PostgreSQL에 데이터 저장
            await self._save_to_database(df)
            
            logger.debug(f"Processed {len(df)} data points for {symbol} on {exchange_name}")
            
        except Exception as e:
            logger.error(f"Error processing data for {symbol} on {exchange_name}: {e}")
            
    async def _send_to_redis_stream(self, df: pd.DataFrame):
        """Redis Streams에 데이터 전송"""
        try:
            for _, row in df.iterrows():
                message_data = {
                    'symbol': row['symbol'],
                    'timestamp': row['timestamp'].isoformat(),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': float(row['volume']),
                    'exchange': row['exchange'],
                    'timeframe': row['timeframe']
                }
                
                # Redis Streams에 메시지 전송
                self.redis_client.xadd(
                    'raw-market-data',
                    {
                        'data': json.dumps(message_data),
                        'timestamp': row['timestamp'].isoformat(),
                        'exchange': row['exchange'],
                        'symbol': row['symbol']
                    }
                )
                
        except Exception as e:
            logger.error(f"Error sending data to Redis stream: {e}")
            
    async def _save_to_database(self, df: pd.DataFrame):
        """PostgreSQL에 데이터 저장"""
        try:
            # 실제 구현에서는 SQLAlchemy를 사용하여 데이터베이스에 저장
            # 여기서는 로깅만 수행
            logger.debug(f"Saving {len(df)} records to database")
            
            # TODO: 실제 데이터베이스 저장 로직 구현
            # from app.models.market_data import MarketDataModel
            # await MarketDataModel.bulk_insert(df)
            
        except Exception as e:
            logger.error(f"Error saving data to database: {e}")
            
    async def get_historical_data(self, symbol: str, exchange_name: str, 
                                start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """과거 데이터 수집"""
        try:
            exchange = self.exchanges.get(exchange_name)
            if not exchange:
                raise ValueError(f"Exchange {exchange_name} not available")
                
            # 날짜를 타임스탬프로 변환
            start_ts = int(start_date.timestamp() * 1000)
            end_ts = int(end_date.timestamp() * 1000)
            
            all_data = []
            current_ts = start_ts
            
            while current_ts < end_ts:
                try:
                    ohlcv = exchange.fetch_ohlcv(symbol, '1m', since=current_ts, limit=1000)
                    if not ohlcv:
                        break
                        
                    all_data.extend(ohlcv)
                    current_ts = ohlcv[-1][0] + 1
                    
                    # Rate limiting
                    await asyncio.sleep(exchange.rateLimit / 1000)
                    
                except Exception as e:
                    logger.warning(f"Error fetching historical data batch: {e}")
                    break
                    
            # DataFrame으로 변환
            df = pd.DataFrame(all_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['symbol'] = symbol
            df['exchange'] = exchange_name
            df['timeframe'] = '1m'
            
            # 중복 제거 및 정렬
            df = df.drop_duplicates(subset=['timestamp']).sort_values('timestamp')
            
            logger.info(f"Collected {len(df)} historical data points for {symbol}")
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
            logger.error(f"Error getting market status for {exchange_name}: {e}")
            raise
            
    async def cleanup(self):
        """서비스 정리"""
        await self.stop_collection()
        
        # 거래소 연결 종료
        for exchange in self.exchanges.values():
            if hasattr(exchange, 'close'):
                await exchange.close()
                
        logger.info("Data collection service cleaned up")
