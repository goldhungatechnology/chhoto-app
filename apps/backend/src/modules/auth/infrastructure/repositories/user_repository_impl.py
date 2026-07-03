from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.repositories.user_repository import IUserRepository
from src.modules.auth.infrastructure.models.user_model import UserModel
from src.shared.infrastructure.repository.base_repository import BaseRepository


class UserRepositoryImpl(BaseRepository[UserEntity], IUserRepository):
    """
    sqlalchemy implementation of the user repository interface
    """

    def __init__(self, session: AsyncSession):
        """Initialize UserRepositoryImpl with an async database session."""
        self.session = session
        self.table_name = UserModel.__tablename__

        super().__init__(session, self.table_name)

    def to_row(self, entity: UserEntity) -> dict:
        """
        convert a user entity to a user model
        """
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "username": entity.username,
            "email": entity.email,
            "avatar_bg": entity.avatar_bg,
            "is_onboarded": entity.is_onboarded,
            "status": entity.status,
            "full_name": entity.full_name,
            "avatar": entity.avatar,
            "phone_number": entity.phone_number,
            "country_id": entity.country_id,
            "email_verified_at": entity.email_verified_at,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> UserEntity:
        """
        convert a user model to a user entity
        """
        return UserEntity(
            id=row["id"],
            uuid=row["uuid"],
            username=row["username"],
            email=row["email"],
            avatar_bg=row["avatar_bg"],
            is_onboarded=row["is_onboarded"],
            status=row["status"],
            full_name=row["full_name"],
            avatar=row["avatar"],
            phone_number=row.get("phone_number"),
            country_id=row.get("country_id"),
            email_verified_at=row["email_verified_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
