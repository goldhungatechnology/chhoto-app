import json
import uuid

import redis.asyncio as redis

from src.gateway.ws.backplane.interface import IBackplane
from collections.abc import AsyncIterator


class RedisBackplane(IBackplane):
    """
    implements the IBackplane interface using Redis as the message broker. It uses Redis Pub/Sub to publish and subscribe to messages. Each instance of the backplane generates a unique instance ID to ensure that messages published by the same instance are not received by that instance.
    """

    def __init__(self, redis_url: str):
        self._redis = redis.from_url(redis_url, decode_responses=True)
        self._pubsub = self._redis.pubsub()
        self._instance_id = uuid.uuid4().hex[:8]

    async def publish(self, channel: str, message: dict) -> None:
        """
        Publish a message to a channel. The message is serialized to JSON and includes the instance ID to prevent the publisher from receiving its own messages.
        """
        message["_sid"] = self._instance_id
        await self._redis.publish(channel, json.dumps(message, default=str))

    async def subscribe(self, patterns: list[str]) -> AsyncIterator[tuple[str, dict]]:
        """
        Subscribe to channels matching the given patterns and yield messages as they arrive. The method returns an asynchronous iterator that yields tuples of (channel, message) for each received message. The backplane ensures that messages published by the same instance are not received by that instance by checking the instance ID in the message payload.
        """
        await self._pubsub.psubscribe(*patterns)
        async for raw in self._pubsub.listen():
            if raw["type"] not in ("pmessage", "message"):
                continue
            payload = json.loads(raw["data"])
            if payload.pop("_sid", None) != self._instance_id:
                yield raw["channel"], payload

    async def close(self) -> None:
        """
        Close the backplane and release any resources. This method should be called when the gateway is shutting down to ensure that all connections to the message broker are properly closed.
        """
        try:
            await self._pubsub.unsubscribe()
            await self._pubsub.reset()
        except Exception:
            pass
        await self._redis.close()
