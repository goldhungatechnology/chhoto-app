from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.domain.entities.user_account_entity import UserAccountEntity
from src.modules.auth.domain.repositories.user_account_repository import (
    IUserAccountRepository,
)
from src.modules.auth.infrastructure.models.user_account_model import UserAccountModel
from src.shared.infrastructure.repository.base_repository import BaseRepository


class UserAccountRepositoryImpl(
    BaseRepository[UserAccountEntity], IUserAccountRepository
):
    """
    SQLAlchemy implementation of the IUserAccountRepository interface.
    """

    def __init__(self, session: AsyncSession):
        """Initialize UserAccountRepositoryImpl with an async database session."""
        self.session = session
        self.table_name = UserAccountModel.__tablename__

        super().__init__(session, self.table_name)

    def to_row(self, entity: UserAccountEntity) -> dict:
        """
        Convert a UserAccountEntity to a dictionary for database insertion.
        """
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "type": entity.type,
            "user_id": entity.user_id,
            "hashed_password": entity.hashed_password,
            "provider": entity.provider,
            "last_password_updated_at": entity.last_password_updated_at,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> UserAccountEntity:
        """
        Convert a database row to a UserAccountEntity.
        """
        return UserAccountEntity(
            id=row["id"],
            uuid=row["uuid"],
            type=row["type"],
            user_id=row["user_id"],
            hashed_password=row.get("hashed_password"),
            provider=row.get("provider"),
            last_password_updated_at=row.get("last_password_updated_at"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
