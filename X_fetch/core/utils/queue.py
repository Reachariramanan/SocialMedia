import json
import redis.asyncio as redis
from typing import Any, Dict, Optional
from core.config.settings import settings
from core.utils.common import setup_logging

logger = setup_logging("QueueSystem")

class QueueSystem:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)

    async def push(self, topic: str, data: Dict[str, Any]):
        try:
            await self.redis.xadd(topic, {"payload": json.dumps(data)})
            logger.debug(f"Pushed message to topic: {topic}")
        except Exception as e:
            logger.error(f"Failed to push to queue {topic}: {e}")

    async def pop(self, topic: str, group: str, consumer: str) -> Optional[Dict[str, Any]]:
        try:
            # Read from Redis Stream
            messages = await self.redis.xreadgroup(group, consumer, {topic: ">"}, count=1)
            if not messages:
                return None
            
            # Parse message
            stream, msgs = messages[0]
            msg_id, payload = msgs[0]
            data = json.loads(payload[b"payload"])
            
            # Acknowledge message
            await self.redis.xack(topic, group, msg_id)
            return data
        except Exception as e:
            logger.error(f"Failed to pop from queue {topic}: {e}")
            return None
