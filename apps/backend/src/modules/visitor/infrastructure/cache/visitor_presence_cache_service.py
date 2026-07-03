import json

from src.modules.visitor.domain.ports.visitor_presence_store import (
    IVisitorPresenceStore,
)
from src.modules.visitor.domain.value_objects.visitor_presence import VisitorPresence
from src.modules.visitor.infrastructure.cache.visitor_cache_keys import VisitorCacheKeys
from src.shared.infrastructure.cache_manager.base_cache_service import BaseCacheService

# Presence is ephemeral: if a visitor stops sending heartbeats the snapshot must
# disappear on its own. Heartbeats arrive every 10-15s, so a 60s TTL tolerates a
# few missed beats before the visitor is treated as gone.
DEFAULT_PRESENCE_TTL = 60


class VisitorPresenceCacheService(BaseCacheService, IVisitorPresenceStore):
    """
    Redis-backed implementation of the visitor presence store.
    """

    def __init__(self):
        super().__init__(cache_manager="redis")
        # Raw redis.asyncio client for operations (SCAN / MGET) not exposed by
        # the generic ICacheManager interface.
        self._redis = self.client.cache_client

    async def get_presence(
        self, *, organization_id: int, visitor_id: int
    ) -> VisitorPresence | None:
        key = VisitorCacheKeys.presence_key(organization_id, visitor_id)
        raw = await self.client.get(key)
        if raw is None:
            return None
        try:
            return VisitorPresence.from_dict(json.loads(raw))
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    async def set_presence(self, presence: VisitorPresence, ttl: int) -> None:
        await self.client.set(
            key=VisitorCacheKeys.presence_key(
                presence.organization_id, presence.visitor_id
            ),
            value=json.dumps(presence.to_dict()),
            ttl=ttl,
        )

    async def touch(
        self, *, organization_id: int, visitor_id: int, last_seen: str, ttl: int
    ) -> bool:
        key = VisitorCacheKeys.presence_key(organization_id, visitor_id)
        raw = await self.client.get(key)
        if raw is None:
            return False
        data = json.loads(raw)
        data["last_seen"] = last_seen
        data["status"] = "active"
        await self.client.set(key=key, value=json.dumps(data), ttl=ttl)
        return True

    async def delete_presence(self, *, organization_id: int, visitor_id: int) -> None:
        await self.client.delete(
            VisitorCacheKeys.presence_key(organization_id, visitor_id)
        )

    async def list_active(self, organization_id: int) -> list[VisitorPresence]:
        pattern = VisitorCacheKeys.presence_scan_pattern(organization_id)
        keys = [key async for key in self._redis.scan_iter(match=pattern, count=200)]
        if not keys:
            return []

        raw_values = await self._redis.mget(keys)
        presences: list[VisitorPresence] = []
        for raw in raw_values:
            if not raw:
                continue
            try:
                presences.append(VisitorPresence.from_dict(json.loads(raw)))
            except (json.JSONDecodeError, KeyError, ValueError):
                # Skip malformed / partially-expired entries rather than failing
                # the whole dashboard read.
                continue
        return presences

    async def set_session_index(
        self, *, session_uuid: str, organization_id: int, visitor_id: int, ttl: int
    ) -> None:
        await self.client.set(
            key=VisitorCacheKeys.session_index_key(session_uuid),
            value=json.dumps(
                {"organization_id": organization_id, "visitor_id": visitor_id}
            ),
            ttl=ttl,
        )

    async def get_session_index(self, session_uuid: str) -> tuple[int, int] | None:
        raw = await self.client.get(VisitorCacheKeys.session_index_key(session_uuid))
        if raw is None:
            return None
        try:
            data = json.loads(raw)
            return int(data["organization_id"]), int(data["visitor_id"])
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    async def delete_session_index(self, session_uuid: str) -> None:
        await self.client.delete(VisitorCacheKeys.session_index_key(session_uuid))
