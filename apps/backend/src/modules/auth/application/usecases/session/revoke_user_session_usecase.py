from src.modules.auth.domain.services.user_session_domain_service import (
    UserSessionDomainService,
)
from src.modules.auth.infrastructure.cache.auth_cache_service import AuthCacheService
from src.shared.exceptions.base_exceptions import (
    DomainError,
    ForbiddenError,
    NotFoundError,
    ServerError,
)
from src.shared.mediator.mediator import mediator


class RevokeUserSessionUseCase:
    """
    Revoke a single user session by its UUID, verifying it belongs to the given user.
    """

    def __init__(
        self,
        user_session_domain_service: UserSessionDomainService,
        cache_service: AuthCacheService,
    ):
        self.user_session_domain_service = user_session_domain_service
        self.cache = cache_service

    async def execute(self, session_uuid: str, user_id: int) -> None:
        try:
            session = await self.user_session_domain_service.get_user_session_by_uuid(
                session_uuid=session_uuid
            )
            if not session:
                raise NotFoundError(error="Session not found")

            if session.user_id != user_id:
                raise ForbiddenError(
                    error="You do not have permission to revoke this session"
                )

            if session.is_revoked() or session.is_expired():
                raise NotFoundError(error="Session not found")

            session.revoke()

            updated_session = (
                await self.user_session_domain_service.update_user_session(session)
            )
            for event in updated_session.pull_events():
                await mediator.publish(event)
            await self.cache.delete_user_session(session.uuid)
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while revoking the session",
                internal_details=str(e),
            ) from e
