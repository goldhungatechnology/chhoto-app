from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from src.modules.workforce.domain.entities.invitation.invitation_entity import (
    InvitationEntity,
)
from src.modules.workforce.domain.repositories.invitation.invitation_repository import (
    IInvitationRepository,
)
from src.modules.workforce.infrastructure.models.invitation.invitation_model import (
    InvitationModel,
)
from src.shared.exceptions.base_exceptions import ServerError
from src.shared.infrastructure.repository.organization_repository import (
    OrganizationRepository,
)


class InvitationRepositoryImpl(
    OrganizationRepository[InvitationEntity], IInvitationRepository
):
    """
    SQLAlchemy implementation of the invitation repository. Inherits the
    organization-scoped query helpers AND the automatic audit writer hooked
    into add/_emit_audit_event — invitation creation will write a row into
    sys_audit_logs with the hashed_token field auto-redacted (the audit
    sanitizer redacts any key containing "token").
    """

    def __init__(self, session: AsyncSession, organization_id: int):
        self.session = session
        self.organization_id = organization_id
        self.table_name = InvitationModel.__tablename__

        super().__init__(
            session=session,
            table_name=self.table_name,
            organization_id=organization_id,
        )

    def to_row(self, entity: InvitationEntity) -> dict:
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "organization_id": entity.organization_id,
            "email": entity.email,
            "role_id": entity.role_id,
            "team_id": entity.team_id,
            "invited_by_id": entity.invited_by_id,
            "hashed_token": entity.hashed_token,
            "status": entity.status,
            "expires_at": entity.expires_at,
            "accepted_at": entity.accepted_at,
            "created_by_id": entity.created_by_id,
            "updated_by_id": entity.updated_by_id,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> InvitationEntity:
        return InvitationEntity(
            id=row["id"],
            uuid=row["uuid"],
            organization_id=row["organization_id"],
            email=row["email"],
            role_id=row["role_id"],
            team_id=row.get("team_id"),
            invited_by_id=row["invited_by_id"],
            hashed_token=row["hashed_token"],
            status=row["status"],
            expires_at=row["expires_at"],
            accepted_at=row.get("accepted_at"),
            created_by_id=row.get("created_by_id"),
            updated_by_id=row.get("updated_by_id"),
            created_at=row["created_at"],
            updated_at=row.get("updated_at"),
        )

    async def get_by_hashed_token(self, hashed_token: str) -> InvitationEntity | None:
        """
        Token lookup is intentionally NOT organization-scoped. Public endpoints
        identify the invitation purely by the token; the token itself proves
        the caller has authority to see the invitation.
        """
        sql = text(
            f"SELECT * FROM {self.table_name} WHERE hashed_token = :hashed_token"
        )
        try:
            result = await self.session.execute(sql, {"hashed_token": hashed_token})
            row = result.mappings().one_or_none()
            return self.to_entity(dict(row)) if row else None
        except Exception as e:
            raise ServerError(
                error="Failed to lookup invitation", internal_details=str(e)
            ) from e

    async def mark_accepted_if_pending(
        self, invitation_id: int
    ) -> InvitationEntity | None:
        """
        Atomically flip a 'pending' invitation to 'accepted'.

        The status guard in the WHERE clause makes acceptance a compare-and-set:
        only the first of two concurrent accepts of the same invitation updates a
        row; the loser gets no row back. This prevents the double-accept race
        that would otherwise create duplicate memberships/role assignments.
        """
        sql = text(
            f"""
            UPDATE {self.table_name}
            SET status = 'accepted', accepted_at = NOW(), updated_at = NOW()
            WHERE id = :id AND status = 'pending'
            RETURNING *
            """
        )
        result = await self.session.execute(sql, {"id": invitation_id})
        row = result.mappings().one_or_none()
        return self.to_entity(dict(row)) if row else None
