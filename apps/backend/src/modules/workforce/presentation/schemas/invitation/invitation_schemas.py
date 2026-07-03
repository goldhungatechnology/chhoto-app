from datetime import datetime

from src.modules.workforce.presentation.schemas.rbac.rbac_role_schemas import (
    CreatedByUserSchema,
)
from src.shared.schemas import BaseSchema, DomainEmail, Field


class CreateInvitationRequestSchema(BaseSchema):
    """
    Schema for issuing a new invitation.
    """

    email: DomainEmail
    role_uuid: str = Field(min_length=1, max_length=255)
    team_uuid: str | None = Field(default=None, min_length=1, max_length=255)


class InvitationResponseSchema(BaseSchema):
    """
    Schema for admin-side invitation listings/responses.
    """

    uuid: str
    email: str
    status: str
    role_id: int
    team_id: int | None
    expires_at: datetime
    accepted_at: datetime | None
    created_at: datetime
    invited_by: CreatedByUserSchema | None = None

    model_config = {
        "from_attributes": True,
    }


class InvitationPreviewResponseSchema(BaseSchema):
    """
    Schema for the public GET /invite/{token} endpoint — minimal data so an
    unauthenticated visitor can decide whether to accept.
    """

    email: str
    organization_name: str
    role_name: str | None
    expires_at: datetime


class AcceptInvitationResponseSchema(BaseSchema):
    """
    Schema returned after a successful acceptance.
    """

    invitation_uuid: str
    organization_uuid: str
    organization_member_uuid: str


class SignupAndAcceptInvitationRequestSchema(BaseSchema):
    """
    Schema for the atomic signup-and-accept flow used when the invitee has
    no account yet. Email is NOT taken from the body — it comes from the
    invitation itself so the user cannot accept under a different email.
    """

    password: str = Field(min_length=8, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)


class SignupAndAcceptInvitationResponseSchema(BaseSchema):
    """
    Schema returned after a successful signup-and-accept. The router converts
    `session_uuid` into a cookie so the frontend is immediately logged in.
    """

    invitation_uuid: str
    organization_uuid: str
    organization_member_uuid: str
    user_uuid: str
    email: str
