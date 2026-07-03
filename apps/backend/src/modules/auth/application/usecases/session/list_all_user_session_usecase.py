from src.modules.auth.domain.entities.user_session_entity import UserSessionEntity
from src.modules.auth.domain.services.user_session_domain_service import (
    UserSessionDomainService,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class ListAllUserSessionUseCase:
    """
    Use case for listing all user sessions.
    """

    def __init__(
        self,
        user_session_domain_service: UserSessionDomainService,
    ):
        self.user_session_domain_service = user_session_domain_service

    async def execute(self, user_id: int) -> list[UserSessionEntity]:
        """
        Executes the use case to list all user sessions for a given user ID.

        1. Retrieves all sessions associated with the specified user ID using the UserSessionDomainService.
        2. Returns a list of UserSessionEntity objects representing the user's sessions.
        """
        try:
            return await self.user_session_domain_service.list_sessions_by_user_id(
                user_id
            )
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while listing user sessions",
                internal_details=str(e),
            ) from e
