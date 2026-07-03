from abc import ABC, abstractmethod
from src.modules.auth.domain.entities.user_entity import UserEntity


class UserReader(ABC):
    """
    user reader port for reading user data.
    """

    @abstractmethod
    async def get_user(self, user_id: int) -> UserEntity | None:
        """
        Retrieves the user session associated with the given session UUID.
        """
        pass

    @abstractmethod
    async def get_users_by_ids(self, user_ids: list[int]) -> list[UserEntity]:
        """
        Retrieves a list of user sessions for the given list of user IDs.
        """
        pass

    @abstractmethod
    async def get_users_by_uuids(self, user_uuids: list[str]) -> list[UserEntity]:
        """
        Retrieves active users for the given list of user UUIDs in a single
        query. Missing or inactive uuids are simply omitted from the result.
        """
        pass
