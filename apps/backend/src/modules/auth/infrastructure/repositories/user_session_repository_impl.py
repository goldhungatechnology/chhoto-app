from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from src.modules.auth.domain.entities.user_session_entity import UserSessionEntity
from src.modules.auth.domain.repositories.user_session_repository import (
    IUserSessionRepository,
)
from src.modules.auth.infrastructure.models.user_session_model import UserSessionModel
from src.shared.exceptions.base_exceptions import ServerError
from src.shared.infrastructure.repository.base_repository import BaseRepository


class UserSessionRepositoryImpl(
    BaseRepository[UserSessionEntity], IUserSessionRepository
):
    """
    SQLALchemy implementation of the IUserSessionRepository interface.
    """

    def __init__(self, session: AsyncSession):
        """Initialize UserSessionRepositoryImpl with an async database session."""
        self.session = session
        self.table_name = UserSessionModel.__tablename__

        super().__init__(session, self.table_name)

    def to_row(self, entity: UserSessionEntity) -> dict:
        """
        Convert a UserSessionEntity to a dictionary for database insertion.
        """
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "user_id": entity.user_id,
            "expires_at": entity.expires_at,
            "device": entity.device,
            "ip_address": entity.ip_address,
            "browser": entity.browser,
            "revoked_at": entity.revoked_at,
            "organization_uuid": entity.organization_uuid,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> UserSessionEntity:
        """
        Convert a database row to a UserSessionEntity.
        """
        return UserSessionEntity(
            id=row["id"],
            uuid=row["uuid"],
            user_id=row["user_id"],
            expires_at=row["expires_at"],
            device=row.get("device"),
            ip_address=row.get("ip_address"),
            browser=row.get("browser"),
            revoked_at=row.get("revoked_at"),
            organization_uuid=row.get("organization_uuid"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def get_latest_session_by_user_id(
        self, user_id: int
    ) -> UserSessionEntity | None:
        """
        Retrieve the latest user session for a given user ID.
        """

        sql = text(
            f"SELECT * FROM {self.table_name} WHERE user_id = :user_id ORDER BY created_at DESC LIMIT 1"
        )

        try:
            result = await self.session.execute(sql, {"user_id": user_id})
            row = result.mappings().one_or_none()
            if row:
                return self.to_entity(dict(row))
            return None
        except Exception as e:
            raise ServerError(
                error="An error occurred while fetching the latest user session",
                internal_details=str(e),
            )
