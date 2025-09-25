# 데이터 분석 에이전트
import pandas as pd
import numpy as np
import ta
from typing import Dict, Any, List
from datetime import datetime
import structlog

from .base_agent import BaseAgent

logger = structlog.get_logger()

class DataAnalysisAgent(BaseAgent):
    """시장 데이터 분석 에이전트"""
    
    def __init__(self, agent_id: str = "data_analysis", redis_url: str = "redis://localhost:6379"):
        super().__init__(agent_id, "DataAnalysisAgent", redis_url)
        self.indicators = {}
        
    async def initialize(self):
        """에이전트 초기화"""
        # 메시지 핸들러 등록
        self.register_handler("NEW_MARKET_DATA", self.handle_new_market_data)
        self.register_handler("HISTORICAL_DATA_READY", self.handle_historical_data)
        self.register_handler("CALCULATE_INDICATORS", self.handle_calculate_indicators)
        self.register_handler("DETECT_ANOMALIES", self.handle_detect_anomalies)
        
    async def cleanup(self):
        """에이전트 정리"""
        pass
        
    async def handle_new_market_data(self, message: Dict[str, Any]):
        """새로운 시장 데이터 처리"""
        try:
            payload = message["payload"]
            symbol = payload.get("symbol")
            data = payload.get("data", [])
            
            logger.info(f"Processing new market data", 
                       symbol=symbol,
                       data_points=len(data))
            
            # DataFrame으로 변환
            df = pd.DataFrame(data)
            if df.empty:
                logger.warning("Empty data received")
                return
                
            # 기술적 지표 계산
            analysis_result = await self.calculate_technical_indicators(df, symbol)
            
            # 전략 에이전트에게 분석 결과 전송
            await self.send_message(
                recipient="strategy_prediction",
                task_name="MARKET_ANALYSIS_RESULT",
                payload={
                    "symbol": symbol,
                    "timestamp": datetime.utcnow().isoformat(),
                    "analysis": analysis_result,
                    "raw_data": data[-10:]  # 최근 10개 데이터만 전송
                },
                correlation_id=message["correlation_id"]
            )
            
            logger.info(f"Market analysis completed", 
                       symbol=symbol,
                       indicators=len(analysis_result))
                       
        except Exception as e:
            logger.error(f"Error processing market data: {e}")
            await self._send_error_response(message, str(e))
            
    async def handle_historical_data(self, message: Dict[str, Any]):
        """과거 데이터 처리"""
        try:
            payload = message["payload"]
            symbol = payload.get("symbol")
            data_path = payload.get("data_path")
            
            logger.info(f"Processing historical data", 
                       symbol=symbol,
                       data_path=data_path)
            
            # 데이터 로드 (실제로는 파일에서 로드)
            # df = pd.read_csv(data_path)
            
            # 여기서는 샘플 데이터 생성
            df = self.generate_sample_data(symbol)
            
            # 전체 데이터셋에 대한 분석
            analysis_result = await self.calculate_technical_indicators(df, symbol)
            
            # 백테스팅을 위한 데이터 준비
            await self.send_message(
                recipient="strategy_prediction",
                task_name="HISTORICAL_ANALYSIS_READY",
                payload={
                    "symbol": symbol,
                    "data_path": data_path,
                    "analysis": analysis_result,
                    "data_points": len(df)
                },
                correlation_id=message["correlation_id"]
            )
            
            logger.info(f"Historical analysis completed", 
                       symbol=symbol,
                       data_points=len(df))
                       
        except Exception as e:
            logger.error(f"Error processing historical data: {e}")
            await self._send_error_response(message, str(e))
            
    async def handle_calculate_indicators(self, message: Dict[str, Any]):
        """지표 계산 요청 처리"""
        try:
            payload = message["payload"]
            symbol = payload.get("symbol")
            data = payload.get("data", [])
            indicator_types = payload.get("indicators", ["rsi", "macd", "sma"])
            
            df = pd.DataFrame(data)
            indicators = {}
            
            for indicator_type in indicator_types:
                if indicator_type == "rsi":
                    indicators["rsi"] = self.calculate_rsi(df)
                elif indicator_type == "macd":
                    macd_data = self.calculate_macd(df)
                    indicators.update(macd_data)
                elif indicator_type == "sma":
                    indicators["sma_20"] = self.calculate_sma(df, 20)
                    indicators["sma_50"] = self.calculate_sma(df, 50)
                    
            await self.send_message(
                recipient=message["sender_agent_id"],
                task_name="INDICATORS_CALCULATED",
                payload={
                    "symbol": symbol,
                    "indicators": indicators,
                    "timestamp": datetime.utcnow().isoformat()
                },
                correlation_id=message["correlation_id"]
            )
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            await self._send_error_response(message, str(e))
            
    async def handle_detect_anomalies(self, message: Dict[str, Any]):
        """이상 징후 감지 처리"""
        try:
            payload = message["payload"]
            symbol = payload.get("symbol")
            data = payload.get("data", [])
            
            df = pd.DataFrame(data)
            anomalies = await self.detect_anomalies(df, symbol)
            
            if anomalies:
                await self.send_message(
                    recipient="master_control",
                    task_name="ANOMALY_DETECTED",
                    payload={
                        "symbol": symbol,
                        "anomalies": anomalies,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    correlation_id=message["correlation_id"]
                )
                
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            await self._send_error_response(message, str(e))
            
    async def calculate_technical_indicators(self, df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
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
            
            # RSI 계산
            indicators["rsi"] = self.calculate_rsi(df)
            
            # MACD 계산
            macd_data = self.calculate_macd(df)
            indicators.update(macd_data)
            
            # 이동평균 계산
            indicators["sma_20"] = self.calculate_sma(df, 20)
            indicators["sma_50"] = self.calculate_sma(df, 50)
            indicators["ema_12"] = self.calculate_ema(df, 12)
            indicators["ema_26"] = self.calculate_ema(df, 26)
            
            # 볼린저 밴드 계산
            bb_data = self.calculate_bollinger_bands(df)
            indicators.update(bb_data)
            
            # 스토캐스틱 계산
            stoch_data = self.calculate_stochastic(df)
            indicators.update(stoch_data)
            
            # 트렌드 분석
            indicators["trend"] = self.analyze_trend(df)
            indicators["volatility"] = self.calculate_volatility(df)
            
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
        except:
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
        except:
            return {"macd": 0.0, "macd_signal": 0.0, "macd_histogram": 0.0}
            
    def calculate_sma(self, df: pd.DataFrame, period: int) -> float:
        """단순 이동평균 계산"""
        try:
            sma = df['close'].rolling(window=period).mean()
            return float(sma.iloc[-1]) if not sma.empty else 0.0
        except:
            return 0.0
            
    def calculate_ema(self, df: pd.DataFrame, period: int) -> float:
        """지수 이동평균 계산"""
        try:
            ema = df['close'].ewm(span=period).mean()
            return float(ema.iloc[-1]) if not ema.empty else 0.0
        except:
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
        except:
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
        except:
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
            
    def generate_sample_data(self, symbol: str) -> pd.DataFrame:
        """샘플 데이터 생성 (테스트용)"""
        import numpy as np
        from datetime import datetime, timedelta
        
        dates = pd.date_range(start=datetime.now() - timedelta(days=100), 
                             end=datetime.now(), freq='1H')
        
        # 랜덤 워크로 가격 데이터 생성
        np.random.seed(42)
        price = 50000
        prices = [price]
        
        for _ in range(len(dates) - 1):
            change = np.random.normal(0, 0.02)  # 2% 표준편차
            price *= (1 + change)
            prices.append(price)
            
        df = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'close': prices,
            'volume': [np.random.uniform(100, 1000) for _ in range(len(dates))],
            'symbol': symbol
        })
        
        return df
