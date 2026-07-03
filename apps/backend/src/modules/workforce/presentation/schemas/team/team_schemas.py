from datetime import datetime
from typing import Literal

from src.modules.workforce.presentation.schemas.rbac.rbac_role_schemas import (
    CreatedByUserSchema,
)
from src.shared.schemas import BaseSchema, Field

# Allowed team-member roles, mirrors TeamMemberRole in the domain layer.
TeamMemberRoleLiteral = Literal["member", "supervisor", "team_lead"]


class CreateTeamRequestSchema(BaseSchema):
    """
    Schema for creating a new team.
    """

    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    color: str | None = Field(default=None, max_length=255)
    timezone: str | None = Field(default=None, max_length=255)


class UpdateTeamRequestSchema(BaseSchema):
    """
    Schema for updating an existing team.
    """

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    color: str | None = Field(default=None, max_length=255)
    timezone: str | None = Field(default=None, max_length=255)
    is_default: bool | None = None


class TeamMemberSummarySchema(BaseSchema):
    """
    Lightweight member representation embedded in a team listing: the member's
    user details plus their role within the team.
    """

    member_id: int
    role: str
    user: CreatedByUserSchema | None = None


class TeamResponseSchema(BaseSchema):
    """
    Schema for team responses.
    """

    uuid: str
    name: str
    description: str | None
    color: str | None
    timezone: str | None
    is_default: bool
    status: str
    created_at: datetime
    created_by: CreatedByUserSchema | None = None
    team_lead: CreatedByUserSchema | None = Field(
        default=None, serialization_alias="team lead"
    )
    members: list[TeamMemberSummarySchema] = []

    model_config = {
        "from_attributes": True,
    }


class TeamListResponseSchema(BaseSchema):
    """
    Paginated container for team listings (items + total + limit + offset).
    """

    items: list[TeamResponseSchema]
    total: int
    limit: int
    offset: int


class SetTeamMemberRoleRequestSchema(BaseSchema):
    """
    Schema for changing a team member's role.
    """

    role: TeamMemberRoleLiteral


class AddTeamMembersRequestSchema(BaseSchema):
    """
    Schema for adding multiple members to a team in one request. Users are
    role-bucketed by user uuid and every bucket is optional, in the shape:
    {"member": [uuid, ...], "supervisor": [uuid, ...], "lead": uuid}.

    `member` and `supervisor` are lists of user uuids; `lead` is a single user
    uuid (a team has at most one lead).
    """

    member: list[str] = []
    supervisor: list[str] = []
    lead: str | None = None


class TeamMemberResponseSchema(BaseSchema):
    """
    Schema for team member responses.

    `member` is the user behind the team membership (resolved via
    org_organization_members.user_id), `added_by` is the user who added them.
    """

    uuid: str
    member_id: int
    role: str
    joined_at: datetime
    member: CreatedByUserSchema | None = None
    added_by: CreatedByUserSchema | None = None

    model_config = {
        "from_attributes": True,
    }


class RelocateTeamMemberDetailsSchema(BaseSchema):
    """
    Schema for relocating a single team member to another team.
    """

    member_id: int
    new_team_uuid: str
    role: TeamMemberRoleLiteral


class RelocateTeamMembersRequestSchema(BaseSchema):
    """
    Schema for relocating team members to another team.
    """

    members: list[RelocateTeamMemberDetailsSchema] = Field(min_length=1)


class CursorPageInfoSchema(BaseSchema):
    """
    Cursor-based pagination metadata.
    """

    prev_cursor: str | None = None
    next_cursor: str | None = None
    has_previous_page: bool = False
    has_next_page: bool = False


class TeamMemberCursorListResponseSchema(BaseSchema):
    """
    Cursor-paginated container for team member listings.
    """

    team_name: str
    total_members: int
    records: list[dict]
    page_info: CursorPageInfoSchema
