from src.modules.auth.domain.entities.user_session_entity import UserSessionEntity
from src.shared.domain.repository.base_repository_interface import IBaseRepository


class IUserSessionRepository(IBaseRepository[UserSessionEntity]):
    """
    Interface for the User session repository.
    """

    async def get_latest_session_by_user_id(
        self, user_id: int
    ) -> UserSessionEntity | None:
        """
        List the latest session for a given user ID.
        """
        raise NotImplementedError
