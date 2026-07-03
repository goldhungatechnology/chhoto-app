from typing import Literal

from src.shared.infrastructure.cache_manager.adapter.redis.redis_cache_manager import (
    RedisCacheManager,
)


class BaseCacheService:
    """
    base cache service
    """

    def __init__(self, cache_manager: Literal["redis", "memcached"]):
        match cache_manager:
            case "redis":
                self.cache_manger = RedisCacheManager()
            case _:
                raise ValueError("Invalid cache manager type")

    @property
    def client(self):
        return self.cache_manger

    def __str__(self) -> str:
        return f"BaseCacheService using {self.cache_manger.__class__.__name__}"
