from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.domain.repositories.user_repository import IUserRepository


class UserRepositoryImpl(IUserRepository):
    """
    SQLAlchemy implementation of the User Repository port.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> None:
        """
        Retrieves user by ID.
        TODO: Query SQLAlchemy model, map results, and return Domain UserEntity.
        """
        pass

    async def get_by_email(self, email: str) -> None:
        """
        Retrieves user by email.
        TODO: Query SQLAlchemy model, map results, and return Domain UserEntity.
        """
        pass

    async def save(self, user: Any) -> None:
        """
        Saves user entity.
        TODO: Convert domain entity to SQLAlchemy model and upsert to database.
        """
        pass

