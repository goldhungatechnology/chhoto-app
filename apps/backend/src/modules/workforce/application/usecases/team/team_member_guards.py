from src.modules.organization.domain.ports.organization_member.organization_member_reader import (
    OrganizationMemberReader,
)
from src.shared.exceptions.base_exceptions import InvalidError


async def ensure_member_belongs_to_org(
    organization_member_reader: OrganizationMemberReader,
    member_id: int,
    organization_id: int,
) -> None:
    """
    Guard against cross-org IDOR: a `member_id` taken from the request body/path
    must resolve to an active membership of the actor's own organization before
    it can be used in any team operation.
    """
    members = await organization_member_reader.get_members_by_ids([member_id])
    member = next((m for m in members if m.id == member_id), None)
    if (
        not member
        or member.organization_id != organization_id
        or member.status != "active"
    ):
        raise InvalidError(
            error="Member not found in this organization",
            internal_details=(
                f"member_id={member_id} does not belong to organization_id="
                f"{organization_id}"
            ),
        )
