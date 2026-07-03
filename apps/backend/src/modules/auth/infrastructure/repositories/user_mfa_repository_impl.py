from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.auth.domain.entities.user_mfa_entity import UserMFAEntity
from src.modules.auth.domain.repositories.user_mfa_repository import IUserMFARepository
from src.modules.auth.infrastructure.models.user_mfa_model import UserMFAModel
from src.shared.infrastructure.repository.base_repository import BaseRepository


class UserMFARepositoryImpl(BaseRepository[UserMFAEntity], IUserMFARepository):
    """
    SQLAlchemy implementation of the IUserMFARepository interface.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize UserMFARepositoryImpl with an async database session.
        """
        self.session = session
        self.table_name = UserMFAModel.__tablename__

    def to_row(self, entity: UserMFAEntity) -> dict:
        """
        Convert a UserMFAEntity to a dictionary for database insertion.
        """
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "user_id": entity.user_id,
            "method": entity.method,
            "secret": entity.secret,
            "revoked_at": entity.revoked_at,
            "verified_at": entity.verified_at,
            "auth_url": entity.auth_url,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> UserMFAEntity:
        """
        Convert a database row to a UserMFAEntity.
        """
        return UserMFAEntity(
            id=row["id"],
            uuid=row["uuid"],
            user_id=row["user_id"],
            method=row["method"],
            secret=row["secret"],
            revoked_at=row.get("revoked_at"),
            verified_at=row.get("verified_at"),
            auth_url=row.get("auth_url"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
