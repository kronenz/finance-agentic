import asyncio
import json
import logging
import uuid
import redis.asyncio as redis
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentCommunicationProtocol:
    """
    Implements a communication protocol for AI agents using Redis Pub/Sub.
    This allows for an event-driven architecture where agents can communicate asynchronously.
    """
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.redis_client = None
        self.pubsub = None
        self.message_handlers = {}

    async def connect(self):
        """Connects to Redis and subscribes to the agent's channel."""
        try:
            logger.info(f"Agent {self.agent_id}: Connecting to communication channel...")
            self.redis_client = await redis.from_url(settings.REDIS_URL)
            self.pubsub = self.redis_client.pubsub()
            # Subscribe to a general channel and a direct channel for this agent
            await self.pubsub.subscribe(f"agent:broadcast", f"agent:{self.agent_id}")
            logger.info(f"Agent {self.agent_id}: Subscribed to communication channels.")
        except Exception as e:
            logger.error(f"Agent {self.agent_id}: Failed to connect to Redis: {e}")
            raise

    async def send_message(self, target_agent_id: str, event: str, data: dict):
        """Sends a message to another agent."""
        message = {
            "message_id": str(uuid.uuid4()),
            "source_agent_id": self.agent_id,
            "event": event,
            "data": data
        }
        channel = f"agent:{target_agent_id}"
        try:
            await self.redis_client.publish(channel, json.dumps(message))
            logger.debug(f"Agent {self.agent_id} sent '{event}' to {target_agent_id}")
        except Exception as e:
            logger.error(f"Agent {self.agent_id}: Failed to send message to {target_agent_id}: {e}")
            # Implement retry or error handling logic here

    async def broadcast_message(self, event: str, data: dict):
        """Broadcasts a message to all agents."""
        message = {
            "message_id": str(uuid.uuid4()),
            "source_agent_id": self.agent_id,
            "event": event,
            "data": data
        }
        channel = "agent:broadcast"
        try:
            await self.redis_client.publish(channel, json.dumps(message))
            logger.debug(f"Agent {self.agent_id} broadcasted '{event}'")
        except Exception as e:
            logger.error(f"Agent {self.agent_id}: Failed to broadcast message: {e}")

    def on_message(self, event: str):
        """Decorator to register a handler for a specific event."""
        def decorator(handler):
            self.message_handlers[event] = handler
            return handler
        return decorator

    async def listen(self):
        """Listens for incoming messages and dispatches them to handlers."""
        if not self.pubsub:
            await self.connect()
        
        logger.info(f"Agent {self.agent_id}: Listening for messages...")
        while True:
            try:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message and isinstance(message['data'], bytes):
                    data = json.loads(message['data'].decode('utf-8'))
                    event = data.get("event")
                    if event in self.message_handlers:
                        await self.message_handlers[event](data)
                    else:
                        logger.warning(f"Agent {self.agent_id}: No handler for event '{event}'")
            except Exception as e:
                logger.error(f"Agent {self.agent_id}: Error while listening for messages: {e}")
                # Add reconnection logic if pubsub connection is lost
                await asyncio.sleep(5)

async def main():
    """Example usage of the AgentCommunicationProtocol."""
    agent1 = AgentCommunicationProtocol(agent_id="agent_001")
    agent2 = AgentCommunicationProtocol(agent_id="agent_002")

    @agent1.on_message("greeting")
    async def handle_greeting(message):
        logger.info(f"Agent 1 received greeting from {message['source_agent_id']}: {message['data']}")
        await agent1.send_message(message['source_agent_id'], "greeting_reply", {"text": "Hello back!"})

    @agent2.on_message("greeting_reply")
    async def handle_reply(message):
        logger.info(f"Agent 2 received reply: {message['data']}")

    await agent1.connect()
    await agent2.connect()

    listener1 = asyncio.create_task(agent1.listen())
    listener2 = asyncio.create_task(agent2.listen())

    await asyncio.sleep(1)
    await agent2.send_message("agent_001", "greeting", {"text": "Hello Agent 1!"})
    
    await asyncio.sleep(2)
    listener1.cancel()
    listener2.cancel()

if __name__ == "__main__":
    asyncio.run(main())