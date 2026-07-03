from dataclasses import dataclass, field
from typing import ClassVar

from src.shared.domain.entity.base_entity import BaseEntity
from src.shared.domain.mixin.audit_mixin import AuditMixin


class TeamMemberRole:
    """
    Allowed role values for a team member. Kept as constants (not an Enum)
    to match the string-typed convention already used by other entities in this
    codebase (e.g. InvitationEntity.status). The role is not enforced as an enum
    at the database level; validation lives in the domain layer.
    """

    MEMBER = "member"
    SUPERVISOR = "supervisor"
    TEAM_LEAD = "team_lead"

    ALL: ClassVar[set[str]] = {MEMBER, SUPERVISOR, TEAM_LEAD}


@dataclass(kw_only=True)
class TeamMemberEntity(BaseEntity, AuditMixin):
    """
    Entity representing the association between a team and an organization member.

    `created_at` represents `joined_at` and `created_by_id` represents `added_by`.
    """

    team_id: int = field(
        metadata={
            "description": "The ID of the team",
            "index": True,
            "on_delete": "cascade",
        }
    )
    member_id: int = field(
        metadata={
            "description": "The ID of the organization member",
            "index": True,
            "on_delete": "cascade",
        }
    )
    role: str = field(
        default=TeamMemberRole.MEMBER,
        metadata={
            "description": (
                "The member's role within the team: 'member', 'supervisor', "
                "or 'team_lead'"
            )
        },
    )

    @property
    def is_team_lead(self) -> bool:
        """
        Convenience flag: whether this member holds the team-lead role.
        """
        return self.role == TeamMemberRole.TEAM_LEAD

    def set_role(self, role: str) -> None:
        """
        Assign a new role to this member.
        """
        self.role = role
