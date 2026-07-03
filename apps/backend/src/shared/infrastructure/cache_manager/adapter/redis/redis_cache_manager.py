import redis.asyncio as redis

from src.core.config.settings import config
from src.shared.infrastructure.cache_manager.interface.cache_manager_interface import (
    ICacheManager,
)
from src.shared.infrastructure.logger import logger


class RedisCacheManager(ICacheManager):
    """
    Redis implementation of cache manager
    """

    def __init__(self):
        r = redis.from_url(config.REDIS_URL, decode_responses=True)
        self.cache_client = r
        self.logger = logger

    async def get(self, key: str):
        value = await self.cache_client.get(key)
        if value:
            self.logger.info(f"[Redis -> Cache HIT] Key: {key}")
            return value

        self.logger.warning(f"[Redis -> Cache MISS] Key: {key}")
        return value

    async def set(self, key: str, value, ttl: int | None = None):
        await self.cache_client.set(key, value, ex=ttl)
        self.logger.info(f"[Redis -> Cache SET] Key: {key} with TTL: {ttl}")

    async def multi_get(self, keys: list[str]):
        values = await self.cache_client.mget(keys)
        self.logger.info(f"[Redis -> Cache MULTI_GET] {len(keys)} keys")
        return values

    async def delete(self, key: str):
        await self.cache_client.delete(key)
        self.logger.error(f"[Redis -> Cache DELETE] Key: {key}")

    async def clear(self):
        await self.cache_client.flushdb()
        self.logger.success("[Redis -> Cache CLEAR] All cache cleared")
