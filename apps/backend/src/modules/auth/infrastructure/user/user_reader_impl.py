from src.modules.auth.auth_container import get_auth_container
from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.ports.user.user_reader import UserReader
from src.modules.auth.domain.services.user_domain_service import UserDomainService
from src.modules.auth.infrastructure.cache.auth_cache_service import AuthCacheService
from src.shared.exceptions.base_exceptions import DomainError, ServerError

from src.shared.infrastructure.db import async_session


class UserReaderImpl(UserReader):
    """
    Implementation of the UserSessionReader port that retrieves user session data from a cache and falls back to a database repository if not found in the cache.
    """

    def __init__(
        self,
        user_domain_service: UserDomainService,
        cache_service: AuthCacheService,
    ):
        self.user_domain_service = user_domain_service
        self.cache = cache_service

    async def get_user(self, user_id: int) -> UserEntity | None:
        """
        1. Retrieves the user session data for a given user ID.
        2. First checks the cache for the user session data.
        3. If the data is not found in the cache, it retrieves it from the
              database using the UserDomainService.
        4. If the data is found in the database and is valid, it stores it in the cache for future requests.
        5. If the data is not found in the database or is invalid, it returns None
        """
        try:
            ## Cache HIT
            cache_user = await self._get_user_from_cache(user_id)
            if cache_user:
                return cache_user

            ## Cache MISS - fetch from database
            user = await self.user_domain_service.get_user_by_id(user_id=user_id)

            if not user or not user.is_active():
                return None

            ## Cache Update - store the user in cache for future requests
            await self.cache.set_user_cache(user_id, user)

            return user
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while retrieving the session",
                internal_details=str(e),
            ) from e

    async def get_users_by_ids(self, user_ids: list[int]) -> list[UserEntity]:
        """
        Retrieves a list of user sessions for the given list of user IDs. It first checks the cache for each user ID and retrieves any missing data from the database.
        """
        users = []
        for user_id in user_ids:
            user = await self.get_user(user_id)
            if user:
                users.append(user)
        return users

    async def get_users_by_uuids(self, user_uuids: list[str]) -> list[UserEntity]:
        """
        Retrieves active users for the given UUIDs. Resolved directly from the
        database (there is no by-uuid cache); only active users are returned.
        """
        return await self.user_domain_service.get_users_by_uuids(user_uuids)

    async def _get_user_from_cache(self, user_id: int) -> UserEntity | None:
        """
        Retrieves the user session data for a given user ID from the cache. If the data is not found in the cache, it returns None.
        """
        return await self.cache.get_user_cache(user_id)


def get_user_reader_impl(session=None) -> UserReaderImpl:
    """
    Factory function to create an instance of UserReaderImpl with its
    dependencies. Pass a request-scoped AsyncSession (AsyncSession is not safe
    to share across concurrent requests); only the legacy container-wiring path
    falls back to creating its own session.
    """
    if session is None:
        session = async_session()
    container = get_auth_container(session=session)
    return UserReaderImpl(
        user_domain_service=container.user_domain_service(),
        cache_service=container.cache_service(),
    )
