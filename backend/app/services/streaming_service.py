import asyncio
import json
import logging
import websockets
import redis.asyncio as redis
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketDataStreamer:
    """
    Connects to cryptocurrency exchanges via WebSockets to stream real-time market data.
    Integrates data from multiple sources and publishes it to a Redis Pub/Sub channel.
    """
    def __init__(self, exchanges: list[str]):
        self.exchanges = exchanges
        self.redis_client = None
        self.connection_tasks = []

    async def connect_redis(self):
        """Establishes connection to Redis."""
        try:
            logger.info("Connecting to Redis...")
            self.redis_client = await redis.from_url(settings.REDIS_URL)
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def _stream_handler(self, exchange_name: str, websocket_url: str):
        """Handles the WebSocket connection for a single exchange."""
        while True:
            try:
                async with websockets.connect(websocket_url) as ws:
                    logger.info(f"Connected to {exchange_name} WebSocket stream.")
                    # Example subscription message (specific to each exchange)
                    subscription_msg = {
                        "method": "SUBSCRIBE",
                        "params": ["btcusdt@trade"],
                        "id": 1
                    }
                    await ws.send(json.dumps(subscription_msg))

                    while True:
                        message = await ws.recv()
                        # Publish message to Redis
                        await self.redis_client.publish(f"market_data:{exchange_name}", message)
                        logger.debug(f"Received from {exchange_name} and published to Redis: {message}")

            except (websockets.ConnectionClosed, websockets.InvalidURI) as e:
                logger.error(f"WebSocket connection error with {exchange_name}: {e}. Retrying in 5 seconds...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"An unexpected error occurred with {exchange_name} stream: {e}")
                await asyncio.sleep(5)

    def start_streaming(self):
        """Starts streaming from all configured exchanges."""
        loop = asyncio.get_event_loop()
        if not self.redis_client:
            loop.run_until_complete(self.connect_redis())

        for exchange in self.exchanges:
            # URLs should be fetched from config
            websocket_url = settings.EXCHANGE_WS_URLS.get(exchange)
            if websocket_url:
                task = loop.create_task(self._stream_handler(exchange, websocket_url))
                self.connection_tasks.append(task)
            else:
                logger.warning(f"WebSocket URL for exchange '{exchange}' not found in settings.")
        
        logger.info("Market data streaming started for all configured exchanges.")

    async def stop_streaming(self):
        """Stops all streaming tasks."""
        for task in self.connection_tasks:
            task.cancel()
        await asyncio.gather(*self.connection_tasks, return_exceptions=True)
        if self.redis_client:
            await self.redis_client.close()
        logger.info("Market data streaming stopped.")

async def main():
    # Example: Stream from Binance and Bybit
    streamer = MarketDataStreamer(exchanges=["binance", "bybit"])
    await streamer.connect_redis()
    streamer.start_streaming()
    
    try:
        # Keep the service running
        await asyncio.sleep(3600)
    finally:
        await streamer.stop_streaming()

if __name__ == "__main__":
    # This would typically be run as part of the main application startup
    # For demonstration, we run it standalone.
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down streamer.")