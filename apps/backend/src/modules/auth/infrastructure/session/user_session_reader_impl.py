from src.modules.auth.domain.entities.user_session_entity import UserSessionEntity
from src.modules.auth.domain.ports.session.user_session_reader import UserSessionReader
from src.modules.auth.domain.services.user_session_domain_service import (
    UserSessionDomainService,
)
from src.modules.auth.infrastructure.cache.auth_cache_service import AuthCacheService
from src.modules.auth.infrastructure.repositories.user_session_repository_impl import (
    UserSessionRepositoryImpl,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class UserSessionReaderImpl(UserSessionReader):
    """
    Implementation of the UserSessionReader port that retrieves user session data from a cache and falls back to a database repository if not found in the cache.
    """

    def __init__(
        self,
        user_session_domain_service: UserSessionDomainService,
        cache_service: AuthCacheService,
    ):
        self.user_session_domain_service = user_session_domain_service
        self.cache = cache_service

    async def get_user_session(self, session_uuid: str) -> UserSessionEntity | None:
        """

        1. Retrieves the session from the cache or database using the UserSessionDomainService.
        2. If the session is found in the cache, returns it immediately.
        3. If the session is not found in the cache, fetches it from the database.
        4. If the session is found in the database and is not expired, stores it in the cache for future requests and returns it.
        5. If the session is not found in the database or is expired, returns None.
        """
        try:
            ## Cache HIT
            cache_session = await self._get_session_from_cache(session_uuid)
            if cache_session:
                return cache_session

            ## Cache MISS - fetch from database
            session = await self.user_session_domain_service.get_user_session_by_uuid(
                session_uuid
            )

            if not session or session.is_expired() or session.is_revoked():
                return None
            ## Cache Update - store the session in cache for future requests
            await self.cache.set_user_session(session.uuid, session)

            return session
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while retrieving the session",
                internal_details=str(e),
            ) from e

    async def _get_session_from_cache(
        self, session_uuid: str
    ) -> UserSessionEntity | None:
        """
        Retrieves the session from the cache.

        1. Checks if the session exists in the cache.
        2. If it exists, returns the session.
        3. If it does not exist, returns None.
        """
        return await self.cache.get_user_session(session_uuid)


def get_user_session_reader_impl(session) -> UserSessionReaderImpl:
    """
    Factory function to create an instance of UserSessionReaderImpl with the
    necessary dependencies injected. The caller MUST pass a request-scoped
    AsyncSession; AsyncSession is not safe to share across concurrent requests.
    """
    return UserSessionReaderImpl(
        user_session_domain_service=UserSessionDomainService(
            repository=UserSessionRepositoryImpl(session=session)
        ),
        cache_service=AuthCacheService(),
    )
