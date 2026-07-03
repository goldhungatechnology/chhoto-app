from src.modules.auth.domain.services.user_session_domain_service import (
    UserSessionDomainService,
)
from src.shared.exceptions.base_exceptions import (
    DomainError,
    ServerError,
    UnAuthorizedError,
)
from src.shared.mediator.mediator import mediator


class LogoutUserUseCase:
    """
    Use case for logging out a user.
    """

    def __init__(self, user_session_domain_service: UserSessionDomainService):
        """
        Initializes the use case with the required domain services.
        """
        self.user_session_domain_service = user_session_domain_service

    async def execute(self, session_uuid: str | None = None):
        """
        Executes the use case to log out a user.
        """
        try:
            if not session_uuid:
                raise UnAuthorizedError(
                    error="Session UUID is required for logging out"
                )
            session = await self.user_session_domain_service.get_user_session_by_uuid(
                session_uuid=session_uuid
            )
            if not session or session.is_expired() or session.is_revoked():
                raise UnAuthorizedError(
                    error="Invalid session while logging out. Session might have expired"
                )

            session.revoke()

            updated_session = (
                await self.user_session_domain_service.update_user_session(session)
            )
            for event in updated_session.pull_events():
                await mediator.publish(event)
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while logging out the user",
                internal_details=str(e),
            ) from e
