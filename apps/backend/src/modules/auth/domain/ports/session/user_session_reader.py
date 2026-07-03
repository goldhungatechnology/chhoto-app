from abc import ABC, abstractmethod
from src.modules.auth.domain.entities.user_session_entity import UserSessionEntity


class UserSessionReader(ABC):
    """
    session reader port for reading user session data.
    """

    @abstractmethod
    async def get_user_session(self, session_uuid: str) -> UserSessionEntity | None:
        """
        Retrieves the user session associated with the given session UUID.
        """
        pass
