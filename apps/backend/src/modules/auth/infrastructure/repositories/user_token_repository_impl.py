from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.auth.domain.entities.user_token_entity import UserTokenEntity
from src.modules.auth.domain.repositories.user_token_repository import (
    IUserTokenRepository,
)
from src.modules.auth.infrastructure.models.user_token_model import UserTokenModel
from src.shared.infrastructure.repository.base_repository import BaseRepository


class UserTokenRepositoryImpl(BaseRepository[UserTokenEntity], IUserTokenRepository):
    """
    SQLALchemy implementation of the IUserTokenRepository interface.
    """

    def __init__(self, session: AsyncSession):
        """Initialize UserSessionRepositoryImpl with an async database session."""
        self.session = session
        self.table_name = UserTokenModel.__tablename__

        super().__init__(session, self.table_name)

    def to_row(self, entity: UserTokenEntity) -> dict:
        """
        Convert a UserTokenEntity to a dictionary for database insertion.
        """
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "user_id": entity.user_id,
            "type": entity.type,
            "token_hash": entity.token_hash,
            "expires_at": entity.expires_at,
            "used_at": entity.used_at,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> UserTokenEntity:
        """
        Convert a database row to a UserTokenEntity.
        """
        return UserTokenEntity(
            id=row["id"],
            uuid=row["uuid"],
            user_id=row["user_id"],
            type=row["type"],
            token_hash=row["token_hash"],
            expires_at=row["expires_at"],
            used_at=row.get("used_at"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
