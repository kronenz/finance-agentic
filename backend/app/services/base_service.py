import asyncio
import redis.asyncio as redis
import structlog

logger = structlog.get_logger()

class BaseService:
    """Base class for services."""

    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.is_running = False

    async def initialize(self):
        """Initializes the service."""
        try:
            await self._test_redis_connection()
            logger.info(f"{self.__class__.__name__} initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize {self.__class__.__name__}: {e}")
            raise

    async def _test_redis_connection(self):
        """Tests the Redis connection."""
        try:
            await self.redis_client.ping()
            logger.info("Redis connection successful")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise

    async def start(self):
        """Starts the service."""
        self.is_running = True
        logger.info(f"{self.__class__.__name__} started")

    async def stop(self):
        """Stops the service."""
        self.is_running = False
        logger.info(f"{self.__class__.__name__} stopped")

    async def cleanup(self):
        """Cleans up the service resources."""
        await self.stop()
        await self.redis_client.close()
        logger.info(f"{self.__class__.__name__} cleaned up")
