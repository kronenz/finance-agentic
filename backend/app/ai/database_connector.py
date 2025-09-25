import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnector:
    """
    Manages the connection to the database for AI agents.
    Handles SQLAlchemy session management, asynchronous operations, and error handling.
    """
    _engine = None
    _session_factory = None

    @classmethod
    async def initialize(cls):
        """
        Initializes the database engine and session factory.
        """
        if cls._engine is None:
            try:
                logger.info("Initializing database connection...")
                cls._engine = create_async_engine(settings.ASYNC_DATABASE_URI, pool_pre_ping=True)
                cls._session_factory = sessionmaker(
                    bind=cls._engine,
                    class_=AsyncSession,
                    expire_on_commit=False
                )
                logger.info("Database connection initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize database connection: {e}")
                raise

    @classmethod
    async def get_session(cls) -> AsyncSession:
        """
        Provides a new database session.
        """
        if cls._session_factory is None:
            await cls.initialize()
        
        session = cls._session_factory()
        try:
            # Optional: Perform a simple query to check connection health
            await session.execute("SELECT 1")
            return session
        except SQLAlchemyError as e:
            logger.error(f"Database connection error: {e}")
            await session.close()
            # Implement reconnection logic if necessary
            await cls.reconnect()
            session = cls._session_factory()
            return session

    @classmethod
    async def close(cls):
        """
        Closes the database engine.
        """
        if cls._engine:
            logger.info("Closing database connection...")
            await cls._engine.dispose()
            cls._engine = None
            cls._session_factory = None
            logger.info("Database connection closed.")

    @classmethod
    async def reconnect(cls):
        """
        Handles reconnection logic.
        """
        logger.info("Attempting to reconnect to the database...")
        await cls.close()
        await asyncio.sleep(5)  # Wait before retrying
        await cls.initialize()

async def main():
    """
    Example usage of the DatabaseConnector.
    """
    await DatabaseConnector.initialize()
    session = await DatabaseConnector.get_session()
    if session:
        try:
            # Example: Perform a query
            logger.info("Successfully obtained a database session.")
            # result = await session.execute("SELECT version()")
            # logger.info(f"Database version: {result.scalar_one()}")
        finally:
            await session.close()
    await DatabaseConnector.close()

if __name__ == "__main__":
    asyncio.run(main())