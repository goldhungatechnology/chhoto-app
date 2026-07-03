from src.modules.workforce.domain.events.team.team_domain_events import (
    TeamMemberAddedEvent,
    TeamMemberRemovedEvent,
    TeamMemberRoleAssignedEvent,
)
from src.shared.mediator.listener import listener

# Team-member writes suppress the automatic repository-level CRUD audit (see
# TeamMemberDomainService); these listeners are the single source of audit for
# team membership, recording the business action rather than the raw row diff.
_ENTITY_TABLE = "org_team_members"


@listener(TeamMemberAddedEvent)
async def audit_on_team_member_added(event: TeamMemberAddedEvent):
    """
    Audit log for a member being added to a team.
    """
    from src.shared.infrastructure.audit.audit_writer import write_audit_event

    await write_audit_event(
        action="team_member_added",
        entity_table=_ENTITY_TABLE,
        entity_id=event.team_member_id,
        before_data=None,
        after_data={
            "organization_id": event.organization_id,
            "team_id": event.team_id,
            "member_id": event.member_id,
            "role": event.role,
        },
    )


@listener(TeamMemberRoleAssignedEvent)
async def audit_on_team_member_role_assigned(event: TeamMemberRoleAssignedEvent):
    """
    Audit log for a team member's role being changed.
    """
    from src.shared.infrastructure.audit.audit_writer import write_audit_event

    await write_audit_event(
        action="team_member_role_changed",
        entity_table=_ENTITY_TABLE,
        entity_id=event.team_member_id,
        before_data=None,
        after_data={
            "organization_id": event.organization_id,
            "team_id": event.team_id,
            "member_id": event.member_id,
            "role": event.role,
        },
    )


@listener(TeamMemberRemovedEvent)
async def audit_on_team_member_removed(event: TeamMemberRemovedEvent):
    """
    Audit log for a member being removed from a team.
    """
    from src.shared.infrastructure.audit.audit_writer import write_audit_event

    await write_audit_event(
        action="team_member_removed",
        entity_table=_ENTITY_TABLE,
        entity_id=event.team_member_id,
        before_data={
            "organization_id": event.organization_id,
            "team_id": event.team_id,
            "member_id": event.member_id,
            "role": event.role,
        },
        after_data=None,
    )


__all__ = [
    "audit_on_team_member_added",
    "audit_on_team_member_role_assigned",
    "audit_on_team_member_removed",
]
