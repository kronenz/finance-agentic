import logging
import pandas as pd
import pandas_ta as ta
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MeanReversionStrategy:
    """
    A mean reversion trading strategy using RSI, Bollinger Bands, and VWAP.
    """
    def __init__(self, symbol: str, parameters: Dict[str, Any]):
        """
        Initializes the strategy with its specific parameters.

        Args:
            symbol: The trading symbol this strategy instance is for.
            parameters: A dictionary of strategy parameters, e.g.,
                        {'rsi_period': 14, 'bb_period': 20, 'bb_stddev': 2,
                         'rsi_oversold': 30, 'rsi_overbought': 70}
        """
        self.symbol = symbol
        self.params = parameters
        self.data = pd.DataFrame()
        self.last_signal = None

        # Validate parameters
        required_keys = {'rsi_period', 'bb_period', 'bb_stddev', 'rsi_oversold', 'rsi_overbought'}
        if not required_keys.issubset(self.params.keys()):
            raise ValueError(f"Missing required strategy parameters: {required_keys - set(self.params.keys())}")

        logger.info(f"Initialized MeanReversionStrategy for {self.symbol} with params: {self.params}")

    def _calculate_indicators(self):
        """
        Calculates all necessary technical indicators for the strategy.
        """
        if self.data.empty or len(self.data) < self.params['bb_period']:
            return

        try:
            # RSI
            self.data['rsi'] = ta.rsi(self.data['close'], length=self.params['rsi_period'])

            # Bollinger Bands
            bbands = ta.bbands(self.data['close'], length=self.params['bb_period'], std=self.params['bb_stddev'])
            self.data['bb_lower'] = bbands[f'BBL_{self.params["bb_period"]}_{self.params["bb_stddev"]}.0']
            self.data['bb_upper'] = bbands[f'BBU_{self.params["bb_period"]}_{self.params["bb_stddev"]}.0']
            self.data['bb_middle'] = bbands[f'BBM_{self.params["bb_period"]}_{self.params["bb_stddev"]}.0']

            # VWAP (requires volume)
            if 'volume' in self.data.columns:
                self.data['vwap'] = ta.vwap(self.data['high'], self.data['low'], self.data['close'], self.data['volume'])
            else:
                self.data['vwap'] = None # Handle case where volume is not available

        except Exception as e:
            logger.error(f"Error calculating indicators for {self.symbol}: {e}", exc_info=True)


    def generate_signal(self, new_candle: Dict[str, float]) -> Optional[str]:
        """
        Processes a new data point (candle) and generates a trading signal.

        Args:
            new_candle: A dictionary representing a new OHLCV candle,
                        e.g., {'open': 60000, 'high': 60100, 'low': 59900,
                               'close': 60050, 'volume': 100}

        Returns:
            A signal string ('BUY', 'SELL', 'HOLD') or None if no signal.
        """
        try:
            # Append new data
            new_df = pd.DataFrame([new_candle])
            self.data = pd.concat([self.data, new_df], ignore_index=True)
            # Limit data size to prevent memory issues
            self.data = self.data.tail(200)

            self._calculate_indicators()

            if self.data.empty or any(col not in self.data.columns for col in ['rsi', 'bb_lower', 'bb_upper']):
                return 'HOLD'

            latest = self.data.iloc[-1]
            signal = 'HOLD'

            # Entry conditions
            is_oversold = latest['rsi'] < self.params['rsi_oversold']
            price_below_bb = latest['close'] < latest['bb_lower']
            price_below_vwap = latest['vwap'] is not None and latest['close'] < latest['vwap']

            if is_oversold and price_below_bb and price_below_vwap:
                signal = 'BUY'

            # Exit/Short conditions
            is_overbought = latest['rsi'] > self.params['rsi_overbought']
            price_above_bb = latest['close'] > latest['bb_upper']
            price_above_vwap = latest['vwap'] is not None and latest['close'] > latest['vwap']

            if is_overbought and price_above_bb and price_above_vwap:
                signal = 'SELL'

            if signal != self.last_signal:
                self.last_signal = signal
                logger.info(f"New signal for {self.symbol}: {signal} | Price: {latest['close']:.2f}, RSI: {latest['rsi']:.2f}, BB_Lower: {latest['bb_lower']:.2f}")
                return signal

            return 'HOLD'

        except Exception as e:
            logger.error(f"Error generating signal for {self.symbol}: {e}", exc_info=True)
            return None

    def update_parameters(self, new_parameters: Dict[str, Any]):
        """
        Dynamically updates the strategy's parameters.

        Args:
            new_parameters: A dictionary with the new parameter values.
        """
        logger.info(f"Updating parameters for {self.symbol} from {self.params} to {new_parameters}")
        self.params.update(new_parameters)
        # Re-calculate indicators with new params
        self._calculate_indicators()


if __name__ == '__main__':
    # Example Usage
    strategy_params = {
        'rsi_period': 14, 'bb_period': 20, 'bb_stddev': 2.0,
        'rsi_oversold': 30, 'rsi_overbought': 70
    }
    strategy = MeanReversionStrategy('BTCUSDT', strategy_params)

    # Simulate receiving some historical data first
    hist_data = [
        {'open': 60000, 'high': 60100, 'low': 59900, 'close': 60050, 'volume': 100}
        for _ in range(25) # At least bb_period
    ]
    for candle in hist_data:
        strategy.generate_signal(candle) # Prime the data

    # Simulate a new candle that might trigger a signal
    print("
--- Testing BUY Signal ---")
    buy_candle = {'open': 59000, 'high': 59100, 'low': 58500, 'close': 58600, 'volume': 200}
    strategy.data.at[len(strategy.data)-2, 'rsi'] = 25 # Manually set for testing
    signal = strategy.generate_signal(buy_candle)
    print(f"Generated Signal: {signal}")

    print("
--- Testing Parameter Update ---")
    strategy.update_parameters({'rsi_oversold': 25})