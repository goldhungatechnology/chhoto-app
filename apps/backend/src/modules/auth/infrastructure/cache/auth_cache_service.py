import json
from datetime import UTC, datetime

from src.core.utils.common import serialize
from src.shared.exceptions.base_exceptions import ServerError
from src.modules.auth.infrastructure.cache.auth_cache_keys import AuthCacheKeys
from src.shared.infrastructure.cache_manager.base_cache_service import BaseCacheService
from src.modules.auth.domain.entities.user_session_entity import UserSessionEntity
from src.modules.auth.domain.entities.user_entity import UserEntity


class AuthCacheService(BaseCacheService):
    """
    Cache service for authentication-related data.
    """

    def __init__(self):
        super().__init__(cache_manager="redis")

    @staticmethod
    def _parse_iso_datetime(raw: str | None) -> datetime | None:
        if raw is None:
            return None
        try:
            normalized = raw.replace("Z", "+00:00")
            return datetime.fromisoformat(normalized)
        except ValueError as e:
            raise ServerError(
                error="Invalid datetime value found in auth cache",
                internal_details=str(e),
            ) from e

    async def set_user_session(
        self, session_uuid: str, value: UserSessionEntity, ttl: int = 3600
    ) -> None:
        """
        Store user session data in cache with a specified TTL (time to live).
        """
        await self.client.set(
            key=AuthCacheKeys.get_user_session_key(session_uuid),
            value=json.dumps(value.to_cache_dict(), default=serialize),
            ttl=ttl,
        )

    async def get_user_session(self, session_uuid: str) -> UserSessionEntity | None:
        """
        Retrieve user session data from cache by session UUID.
        """
        data = await self.client.get(
            key=AuthCacheKeys.get_user_session_key(session_uuid),
        )
        if data is None:
            return None
        payload = json.loads(data)
        payload["expires_at"] = self._parse_iso_datetime(payload.get("expires_at"))
        payload["revoked_at"] = self._parse_iso_datetime(payload.get("revoked_at"))
        payload["created_at"] = self._parse_iso_datetime(payload.get("created_at"))
        payload["updated_at"] = self._parse_iso_datetime(payload.get("updated_at"))
        return UserSessionEntity(**payload)

    async def delete_user_session(self, session_uuid: str) -> None:
        """
        Delete user session data from cache by session UUID.
        """
        await self.client.delete(
            key=AuthCacheKeys.get_user_session_key(session_uuid),
        )

    async def set_user_cache(
        self, user_id: int, value: UserEntity, ttl: int = 3600
    ) -> None:
        """
        Store user data in cache with a specified TTL (time to live).
        """
        await self.client.set(
            key=AuthCacheKeys.get_user_cache_key(user_id),
            value=json.dumps(value.to_cache_dict(), default=serialize),
            ttl=ttl,
        )

    async def get_user_cache(self, user_id: int) -> UserEntity | None:
        """
        Retrieve user data from cache by user ID.
        """
        data = await self.client.get(
            key=AuthCacheKeys.get_user_cache_key(user_id),
        )
        if data is None:
            return None
        payload = json.loads(data)
        payload["email_verified_at"] = self._parse_iso_datetime(
            payload.get("email_verified_at")
        )
        payload["created_at"] = self._parse_iso_datetime(payload.get("created_at"))
        payload["updated_at"] = self._parse_iso_datetime(payload.get("updated_at"))
        payload["deleted_at"] = self._parse_iso_datetime(payload.get("deleted_at"))
        return UserEntity(**payload)

    async def delete_user_cache(self, user_id: int) -> None:
        """
        Delete user data from cache by user ID.
        """
        await self.client.delete(
            key=AuthCacheKeys.get_user_cache_key(user_id),
        )

    async def set_user_last_seen(self, user_id: int, ttl: int = 300) -> None:
        """
        Store the current timestamp as the user's last seen time in Redis.
        Default TTL is 5 minutes (300 seconds).
        """
        now = datetime.now(UTC).isoformat()
        await self.client.set(
            key=AuthCacheKeys.get_user_last_seen_key(user_id),
            value=now,
            ttl=ttl,
        )

    async def get_user_last_seen(self, user_id: int) -> datetime | None:
        """
        Retrieve the user's last seen timestamp from Redis.
        Returns None if no timestamp is stored (user is offline or never seen).
        """
        data = await self.client.get(
            key=AuthCacheKeys.get_user_last_seen_key(user_id),
        )
        if data is None:
            return None
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        return datetime.fromisoformat(data)

    async def are_users_online(
        self, user_ids: list[int], threshold_seconds: int = 60
    ) -> dict[int, bool]:
        """
        Check online status for multiple users in batch using MGET.
        Returns {user_id: bool} mapping.
        """
        keys = [AuthCacheKeys.get_user_last_seen_key(uid) for uid in user_ids]
        raw_values = await self.client.multi_get(keys)
        now = datetime.now(UTC)
        result: dict[int, bool] = {}
        for user_id, raw in zip(user_ids, raw_values):
            if raw is None:
                result[user_id] = False
            else:
                if isinstance(raw, bytes):
                    raw = raw.decode("utf-8")
                last_seen = datetime.fromisoformat(raw)
                result[user_id] = (now - last_seen).total_seconds() < threshold_seconds
        return result

    async def is_user_online(self, user_id: int, threshold_seconds: int = 60) -> bool:
        """
        Check if a user is online based on their last seen timestamp.
        A user is considered online if last_seen is within threshold_seconds.
        Default threshold is 1 minute (60 seconds).
        """
        last_seen = await self.get_user_last_seen(user_id)
        if last_seen is None:
            return False
        return (datetime.now(UTC) - last_seen).total_seconds() < threshold_seconds
