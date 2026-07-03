from datetime import UTC, datetime
from src.modules.auth.domain.entities.user_session_entity import UserSessionEntity
from src.modules.auth.domain.events.auth_session_domain_events import (
    UserSessionUpdatedEvent,
)
from src.modules.auth.domain.repositories.user_session_repository import (
    IUserSessionRepository,
)
from src.shared.exceptions.base_exceptions import CreateError


class UserSessionDomainService:
    """
    service class for user session domain logic
    """

    def __init__(self, repository: IUserSessionRepository):
        self.repository = repository

    async def create_user_session(
        self, session_entity: UserSessionEntity
    ) -> UserSessionEntity:
        """
        creates a new user session
        """
        try:
            return await self.repository.add(session_entity)
        except Exception as e:
            raise CreateError(
                error="Failed to create user session", internal_details=str(e)
            ) from e

    async def get_user_session_by_uuid(
        self, session_uuid: str
    ) -> UserSessionEntity | None:
        """
        retrieves a user session by its UUID
        """
        try:
            return await self.repository.get_by_uuid(session_uuid)
        except Exception as e:
            raise CreateError(
                error="Failed to retrieve user session", internal_details=str(e)
            ) from e

    async def list_sessions_by_user_id(self, user_id: int) -> list[UserSessionEntity]:
        """
        lists all sessions for a given user ID
        """
        try:
            return await self.repository.filter(
                user_id=user_id,
                expires_at__gt=datetime.now(UTC),
                revoked_at=None,
            )
        except Exception as e:
            raise CreateError(
                error="Failed to list user sessions", internal_details=str(e)
            ) from e

    async def update_user_session(
        self, session_entity: UserSessionEntity
    ) -> UserSessionEntity:
        """
        updates an existing user session
        """
        try:
            updated_session = await self.repository.update(session_entity)
            updated_session.add_event(
                UserSessionUpdatedEvent(session_uuid=updated_session.uuid)
            )
            return updated_session
        except Exception as e:
            raise CreateError(
                error="Failed to update user session", internal_details=str(e)
            ) from e

    async def get_latest_session_by_user_id(
        self, user_id: int
    ) -> UserSessionEntity | None:
        """
        retrieves the latest session for a given user ID
        """
        try:
            return await self.repository.get_latest_session_by_user_id(user_id)
        except Exception as e:
            raise CreateError(
                error="Failed to retrieve latest user session",
                internal_details=str(e),
            ) from e
