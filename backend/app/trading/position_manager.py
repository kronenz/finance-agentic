import logging
from typing import Dict, Any, Optional
import asyncio
import redis.asyncio as redis

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PositionManager:
    """
    Manages trading positions, calculates real-time P&L, and monitors risk.
    """
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379, risk_limit_usd: float = 1000.0):
        """
        Initializes the PositionManager.

        Args:
            redis_host: The hostname of the Redis server for market data.
            redis_port: The port of the Redis server.
            risk_limit_usd: The maximum allowed loss per position in USD.
        """
        self.positions: Dict[str, Dict[str, Any]] = {}  # Key: symbol
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.risk_limit_usd = risk_limit_usd

    async def update_position(self, symbol: str, quantity: float, entry_price: float):
        """
        Updates a position after a trade execution.

        Args:
            symbol: The trading symbol (e.g., 'BTCUSDT').
            quantity: The amount traded (+ for buy, - for sell).
            entry_price: The price at which the trade was executed.
        """
        if symbol not in self.positions:
            self.positions[symbol] = {'quantity': 0, 'average_entry_price': 0, 'unrealized_pnl': 0}

        pos = self.positions[symbol]
        current_value = pos['quantity'] * pos['average_entry_price']
        trade_value = quantity * entry_price

        new_quantity = pos['quantity'] + quantity

        if new_quantity == 0:
            # Position closed
            self.positions.pop(symbol, None)
            logger.info(f"Position for {symbol} closed.")
        else:
            new_average_price = (current_value + trade_value) / new_quantity
            pos['quantity'] = new_quantity
            pos['average_entry_price'] = new_average_price
            logger.info(f"Updated position for {symbol}: {pos}")

    async def _calculate_pnl(self):
        """
        Periodically calculates and updates the P&L for all open positions.
        """
        while True:
            await asyncio.sleep(1) # Update P&L every second
            for symbol, pos in self.positions.items():
                try:
                    latest_price_str = await self.redis_client.get(f"latest_price:{symbol}")
                    if latest_price_str:
                        latest_price = float(latest_price_str)
                        market_value = pos['quantity'] * latest_price
                        cost_basis = pos['quantity'] * pos['average_entry_price']
                        pnl = market_value - cost_basis
                        pos['unrealized_pnl'] = pnl
                        logger.debug(f"P&L for {symbol}: {pnl:.2f} USD")
                        await self._monitor_risk(symbol, pnl)
                except (ValueError, TypeError) as e:
                    logger.error(f"Could not parse latest price for {symbol}: {e}")
                except Exception as e:
                    logger.error(f"Error calculating P&L for {symbol}: {e}")

    async def _monitor_risk(self, symbol: str, pnl: float):
        """
        Monitors the risk of a position and sends alerts if limits are breached.

        Args:
            symbol: The symbol of the position.
            pnl: The current unrealized P&L of the position.
        """
        if pnl < -self.risk_limit_usd:
            logger.critical(f"RISK ALERT: Loss for {symbol} has exceeded limit! P&L: {pnl:.2f} USD")
            # In a real system, this would trigger an action, e.g., close the position.

    def get_position_sizing(self, symbol: str, risk_per_trade: float = 0.01) -> float:
        """
        Calculates position size based on a simple risk percentage model.
        This is a simplified example. A real implementation would be more complex.

        Args:
            symbol: The trading symbol.
            risk_per_trade: The fraction of total capital to risk on this trade.

        Returns:
            The suggested position size in the base currency.
        """
        # This is a placeholder for a more sophisticated algorithm.
        # It should consider account balance, volatility, stop-loss distance, etc.
        # For now, returning a fixed size for demonstration.
        if "BTC" in symbol:
            return 0.01 # e.g., 0.01 BTC
        return 1.0 # e.g., 1 ETH

    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the current state of a position.

        Args:
            symbol: The trading symbol.

        Returns:
            A dictionary with position details or None if no position exists.
        """
        return self.positions.get(symbol)

    async def run(self):
        """
        Starts the P&L calculation and risk monitoring loop.
        """
        logger.info("Starting Position Manager...")
        asyncio.create_task(self._calculate_pnl())

if __name__ == '__main__':
    async def main():
        pm = PositionManager(risk_limit_usd=50.0)
        # Simulate a buy order fill
        await pm.update_position('BTCUSDT', 0.1, 60000)
        # Start the P&L calculation
        asyncio.create_task(pm.run())
        # Simulate price updates from Redis (for testing)
        redis_client = redis.Redis(decode_responses=True)
        await redis_client.set('latest_price:BTCUSDT', 60100)
        await asyncio.sleep(2)
        print(f"Position: {pm.get_position('BTCUSDT')}")
        await redis_client.set('latest_price:BTCUSDT', 59400) # Price drops
        await asyncio.sleep(2)
        print(f"Position: {pm.get_position('BTCUSDT')}") # Should trigger risk alert
        await redis_client.close()

    asyncio.run(main())
