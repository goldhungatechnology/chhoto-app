from abc import ABC, abstractmethod


class ICacheManager(ABC):
    """
    interfaces for cache manager
    """

    @abstractmethod
    async def get(self, key: str):
        """
        get value from cache by key
        """
        raise NotImplementedError

    @abstractmethod
    async def set(self, key: str, value, ttl: int | None = None):
        """
        set value to cache by key with optional time to live (ttl)
        """
        raise NotImplementedError

    @abstractmethod
    async def multi_get(self, keys: list[str]):
        """
        get multiple values from cache by keys
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str):
        """
        delete value from cache by key
        """
        raise NotImplementedError

    @abstractmethod
    async def clear(self):
        """
        clear all cache
        """
        raise NotImplementedError
