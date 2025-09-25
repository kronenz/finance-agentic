# 데이터 분석 서비스
import pandas as pd
import numpy as np
import ta
import redis
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import structlog

from app.services.base_service import BaseService

logger = structlog.get_logger()

class DataAnalysisService(BaseService):
    """시장 데이터 분석 및 특성 엔지니어링 서비스"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        super().__init__(redis_url)
        self.analysis_tasks = {}
        
    async def initialize(self):
        """서비스 초기화"""
        await super().initialize()
        try:
            # 메시지 수신 루프 시작
            self.analysis_task = asyncio.create_task(self._message_loop())
            
            logger.info("Data analysis service message loop started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start data analysis service message loop: {e}")
            raise
            
    async def _message_loop(self):
        """메시지 수신 및 처리 루프"""
        while self.is_running:
            try:
                # Redis Streams에서 메시지 수신
                messages = self.redis_client.xread(
                    {f"raw-market-data": "$"},
                    count=10,
                    block=1000  # 1초 대기
                )
                
                for stream, msgs in messages:
                    for msg_id, fields in msgs:
                        await self._process_message(msg_id, fields)
                        
            except Exception as e:
                logger.error(f"Error in message loop: {e}")
                await asyncio.sleep(1)
                
    async def _process_message(self, msg_id: str, fields: Dict[str, Any]):
        """메시지 처리"""
        try:
            # 메시지 파싱
            data = json.loads(fields.get(b'data', b'{}'))
            
            if not data:
                return
                
            # DataFrame으로 변환
            df = pd.DataFrame([data])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # 기술적 지표 계산
            analysis_result = await self.calculate_technical_indicators(df)
            
            # 분석 결과를 Redis Streams에 전송
            await self._send_analysis_result(data, analysis_result)
            
            # ACK 전송
            self.redis_client.xack("raw-market-data", "analysis_group", msg_id)
            
            logger.debug(f"Processed message {msg_id}")
            
        except Exception as e:
            logger.error(f"Error processing message {msg_id}: {e}")
            
    async def calculate_technical_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """기술적 지표 계산"""
        try:
            if df.empty or len(df) < 20:
                return {}
                
            # 기본 OHLCV 컬럼 확인
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_columns):
                logger.error(f"Missing required columns: {required_columns}")
                return {}
                
            # 가격 데이터 정리
            df = df.copy()
            df = df.dropna()
            
            if len(df) < 20:
                logger.warning(f"Insufficient data for analysis: {len(df)} rows")
                return {}
                
            indicators = {}
            
            # 병렬로 지표 계산
            results = await asyncio.gather(
                self.calculate_rsi(df),
                self.calculate_macd(df),
                self.calculate_sma(df, 20),
                self.calculate_sma(df, 50),
                self.calculate_ema(df, 12),
                self.calculate_ema(df, 26),
                self.calculate_bollinger_bands(df),
                self.calculate_stochastic(df),
                self.analyze_trend(df),
                self.calculate_volatility(df)
            )
            
            rsi, macd, sma_20, sma_50, ema_12, ema_26, bb, stoch, trend, volatility = results
            
            indicators["rsi"] = rsi
            indicators.update(macd)
            indicators["sma_20"] = sma_20
            indicators["sma_50"] = sma_50
            indicators["ema_12"] = ema_12
            indicators["ema_26"] = ema_26
            indicators.update(bb)
            indicators.update(stoch)
            indicators["trend"] = trend
            indicators["volatility"] = volatility
            
            # 신호 생성
            indicators["signals"] = self.generate_signals(df, indicators)
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return {}
            
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> float:
        """RSI 계산"""
        try:
            rsi = ta.momentum.RSIIndicator(df['close'], window=period).rsi()
            return float(rsi.iloc[-1]) if not rsi.empty else 50.0
        except (IndexError, TypeError, ValueError) as e:
            logger.warning(f"Could not calculate RSI: {e}")
            return 50.0
            
    def calculate_macd(self, df: pd.DataFrame) -> Dict[str, float]:
        """MACD 계산"""
        try:
            macd_indicator = ta.trend.MACD(df['close'])
            return {
                "macd": float(macd_indicator.macd().iloc[-1]) if not macd_indicator.macd().empty else 0.0,
                "macd_signal": float(macd_indicator.macd_signal().iloc[-1]) if not macd_indicator.macd_signal().empty else 0.0,
                "macd_histogram": float(macd_indicator.macd_diff().iloc[-1]) if not macd_indicator.macd_diff().empty else 0.0
            }
        except (IndexError, TypeError, ValueError) as e:
            logger.warning(f"Could not calculate MACD: {e}")
            return {"macd": 0.0, "macd_signal": 0.0, "macd_histogram": 0.0}
            
    def calculate_sma(self, df: pd.DataFrame, period: int) -> float:
        """단순 이동평균 계산"""
        try:
            sma = df['close'].rolling(window=period).mean()
            return float(sma.iloc[-1]) if not sma.empty else 0.0
        except (IndexError, TypeError, ValueError) as e:
            logger.warning(f"Could not calculate SMA: {e}")
            return 0.0
            
    def calculate_ema(self, df: pd.DataFrame, period: int) -> float:
        """지수 이동평균 계산"""
        try:
            ema = df['close'].ewm(span=period).mean()
            return float(ema.iloc[-1]) if not ema.empty else 0.0
        except (IndexError, TypeError, ValueError) as e:
            logger.warning(f"Could not calculate EMA: {e}")
            return 0.0
            
    def calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std: float = 2) -> Dict[str, float]:
        """볼린저 밴드 계산"""
        try:
            bb_indicator = ta.volatility.BollingerBands(df['close'], window=period, window_dev=std)
            return {
                "bb_upper": float(bb_indicator.bollinger_hband().iloc[-1]) if not bb_indicator.bollinger_hband().empty else 0.0,
                "bb_middle": float(bb_indicator.bollinger_mavg().iloc[-1]) if not bb_indicator.bollinger_mavg().empty else 0.0,
                "bb_lower": float(bb_indicator.bollinger_lband().iloc[-1]) if not bb_indicator.bollinger_lband().empty else 0.0
            }
        except (IndexError, TypeError, ValueError) as e:
            logger.warning(f"Could not calculate Bollinger Bands: {e}")
            return {"bb_upper": 0.0, "bb_middle": 0.0, "bb_lower": 0.0}
            
    def calculate_stochastic(self, df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Dict[str, float]:
        """스토캐스틱 계산"""
        try:
            stoch_indicator = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'], 
                                                             window=k_period, smooth_window=d_period)
            return {
                "stoch_k": float(stoch_indicator.stoch().iloc[-1]) if not stoch_indicator.stoch().empty else 50.0,
                "stoch_d": float(stoch_indicator.stoch_signal().iloc[-1]) if not stoch_indicator.stoch_signal().empty else 50.0
            }
        except (IndexError, TypeError, ValueError) as e:
            logger.warning(f"Could not calculate Stochastic Oscillator: {e}")
            return {"stoch_k": 50.0, "stoch_d": 50.0}
            
    def analyze_trend(self, df: pd.DataFrame) -> str:
        """트렌드 분석"""
        try:
            if len(df) < 50:
                return "NEUTRAL"
                
            sma_20 = df['close'].rolling(window=20).mean().iloc[-1]
            sma_50 = df['close'].rolling(window=50).mean().iloc[-1]
            current_price = df['close'].iloc[-1]
            
            if current_price > sma_20 > sma_50:
                return "BULLISH"
            elif current_price < sma_20 < sma_50:
                return "BEARISH"
            else:
                return "NEUTRAL"
        except:
            return "NEUTRAL"
            
    def calculate_volatility(self, df: pd.DataFrame, period: int = 20) -> float:
        """변동성 계산"""
        try:
            returns = df['close'].pct_change().dropna()
            volatility = returns.rolling(window=period).std().iloc[-1]
            return float(volatility) if not pd.isna(volatility) else 0.0
        except:
            return 0.0
            
    def generate_signals(self, df: pd.DataFrame, indicators: Dict[str, Any]) -> Dict[str, str]:
        """거래 신호 생성"""
        try:
            signals = {}
            
            # RSI 신호
            rsi = indicators.get("rsi", 50)
            if rsi > 70:
                signals["rsi"] = "SELL"
            elif rsi < 30:
                signals["rsi"] = "BUY"
            else:
                signals["rsi"] = "HOLD"
                
            # MACD 신호
            macd = indicators.get("macd", 0)
            macd_signal = indicators.get("macd_signal", 0)
            if macd > macd_signal:
                signals["macd"] = "BUY"
            elif macd < macd_signal:
                signals["macd"] = "SELL"
            else:
                signals["macd"] = "HOLD"
                
            # 종합 신호
            buy_signals = sum(1 for signal in signals.values() if signal == "BUY")
            sell_signals = sum(1 for signal in signals.values() if signal == "SELL")
            
            if buy_signals > sell_signals:
                signals["overall"] = "BUY"
            elif sell_signals > buy_signals:
                signals["overall"] = "SELL"
            else:
                signals["overall"] = "HOLD"
                
            return signals
            
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
            return {"overall": "HOLD"}
            
    async def _send_analysis_result(self, original_data: Dict, analysis_result: Dict):
        """분석 결과를 Redis Streams에 전송"""
        try:
            # 분석 결과와 원본 데이터를 결합
            result_data = {
                **original_data,
                "analysis": analysis_result,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            # Redis Streams에 메시지 전송
            self.redis_client.xadd(
                'processed-features',
                {
                    'data': json.dumps(result_data),
                    'timestamp': datetime.utcnow().isoformat(),
                    'exchange': original_data.get('exchange', 'unknown'),
                    'symbol': original_data.get('symbol', 'unknown')
                }
            )
            
            logger.debug(f"Analysis result sent for {original_data.get('symbol')}")
            
        except Exception as e:
            logger.error(f"Error sending analysis result: {e}")
            
    async def detect_anomalies(self, df: pd.DataFrame, symbol: str) -> List[Dict[str, Any]]:
        """이상 징후 감지"""
        try:
            anomalies = []
            
            if len(df) < 10:
                return anomalies
                
            # 가격 급등/급락 감지
            price_change = df['close'].pct_change().iloc[-1]
            if abs(price_change) > 0.1:  # 10% 이상 변화
                anomalies.append({
                    "type": "PRICE_SPIKE",
                    "severity": "HIGH" if abs(price_change) > 0.2 else "MEDIUM",
                    "value": price_change,
                    "timestamp": df['timestamp'].iloc[-1] if 'timestamp' in df.columns else None
                })
                
            # 거래량 급증 감지
            volume_avg = df['volume'].rolling(window=20).mean().iloc[-1]
            current_volume = df['volume'].iloc[-1]
            if current_volume > volume_avg * 3:  # 평균의 3배 이상
                anomalies.append({
                    "type": "VOLUME_SPIKE",
                    "severity": "HIGH",
                    "value": current_volume / volume_avg,
                    "timestamp": df['timestamp'].iloc[-1] if 'timestamp' in df.columns else None
                })
                
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []
            
    async def stop(self):
        """서비스 중지"""
        self.is_running = False
        
        if hasattr(self, 'analysis_task'):
            self.analysis_task.cancel()
            try:
                await self.analysis_task
            except asyncio.CancelledError:
                pass
                
        logger.info("Data analysis service stopped")
        
    async def cleanup(self):
        """서비스 정리"""
        await self.stop()
        logger.info("Data analysis service cleaned up")
