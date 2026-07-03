from src.modules.auth.domain.services.user_session_domain_service import (
    UserSessionDomainService,
)
from src.modules.auth.infrastructure.cache.auth_cache_service import AuthCacheService
from src.shared.exceptions.base_exceptions import (
    DomainError,
    ServerError,
)
from src.shared.mediator.mediator import mediator


class RevokeAllUserSessionsUseCase:
    """
    Revoke all user sessions for a given user ID, except for the session with the provided UUID (if any). This is useful for scenarios like password changes or account recovery, where you want to ensure that all other sessions are invalidated.
    """

    def __init__(
        self,
        user_session_domain_service: UserSessionDomainService,
        cache_service: AuthCacheService,
    ):
        self.user_session_domain_service = user_session_domain_service
        self.cache = cache_service

    async def execute(
        self, user_id: int, except_session_uuid: str | None = None
    ) -> int:
        """
        Revokes all user sessions for the specified user ID, except for the session with the provided UUID (if any).
        """
        try:
            sessions = await self.user_session_domain_service.list_sessions_by_user_id(
                user_id
            )

            if except_session_uuid:
                sessions = [s for s in sessions if s.uuid != except_session_uuid]

            if not sessions:
                return 0

            for session in sessions:
                session.revoke()
                updated_session = (
                    await self.user_session_domain_service.update_user_session(session)
                )
                for event in updated_session.pull_events():
                    await mediator.publish(event)
                await self.cache.delete_user_session(session.uuid)

            return len(sessions)
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while revoking all user sessions",
                internal_details=str(e),
            ) from e
