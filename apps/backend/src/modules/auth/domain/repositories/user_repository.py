from abc import ABC, abstractmethod
from typing import Any

# TODO: Import UserEntity once implemented


class IUserRepository(ABC):
    """
    Interface for user domain repository operations.
    """

    @abstractmethod
    async def get_by_id(self, user_id: Any) -> Any:
        """Retrieve a user by ID."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Any:
        """Retrieve a user by email."""
        pass

    @abstractmethod
    async def save(self, user: Any) -> Any:
        """Save/Update a user entity."""
        pass
