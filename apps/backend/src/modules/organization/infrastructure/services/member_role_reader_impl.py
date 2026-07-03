from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.organization.domain.ports.member_role.member_role_reader import (
    MemberRoleReader,
)


class MemberRoleReaderImpl(MemberRoleReader):
    """
    Reads member → role mappings by joining org_member_roles with org_roles.
    Members without an assigned role are omitted from the result (reported as None).
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_member_roles(self, member_ids: list[int]) -> dict[int, str | None]:
        if not member_ids:
            return {}

        sql = text(
            """
            SELECT mr.member_id, r.name
            FROM org_member_roles mr
            JOIN org_roles r ON r.id = mr.role_id
            WHERE mr.member_id = ANY(:member_ids)
              AND r.deleted_at IS NULL
            """
        )
        result = await self.session.execute(sql, {"member_ids": member_ids})
        rows = result.mappings().all()

        roles: dict[int, str | None] = {mid: None for mid in member_ids}
        for row in rows:
            roles[row["member_id"]] = row["name"]
        return roles


def get_member_role_reader(session: AsyncSession) -> MemberRoleReaderImpl:
    """
    Factory function to create a MemberRoleReaderImpl bound to the caller's
    session.
    """
    return MemberRoleReaderImpl(session=session)
