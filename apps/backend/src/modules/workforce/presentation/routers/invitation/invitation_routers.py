from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils.response import CustomResponse as cr
from src.core.utils.response import CustomSuccessResponseSchema, get_cookie_response
from src.modules.workforce.application.usecases.invitation.accept_invitation_usecase import (
    AcceptInvitationUseCase,
)
from src.modules.workforce.application.usecases.invitation.create_invitation_usecase import (
    CreateInvitationUseCase,
)
from src.modules.workforce.application.usecases.invitation.get_invitation_by_token_usecase import (
    GetInvitationByTokenUseCase,
)
from src.modules.workforce.application.usecases.invitation.list_invitations_usecase import (
    ListInvitationsUseCase,
)
from src.modules.workforce.application.usecases.invitation.resend_invitation_usecase import (
    ResendInvitationUseCase,
)
from src.modules.workforce.application.usecases.invitation.revoke_invitation_usecase import (
    RevokeInvitationUseCase,
)
from src.modules.workforce.application.usecases.invitation.signup_and_accept_invitation_usecase import (
    SignupAndAcceptInvitationUseCase,
)
from src.modules.workforce.infrastructure.uow.workforce_uow import WorkforceUOW
from src.modules.workforce.presentation.schemas.invitation.invitation_schemas import (
    AcceptInvitationResponseSchema,
    CreateInvitationRequestSchema,
    InvitationPreviewResponseSchema,
    InvitationResponseSchema,
    SignupAndAcceptInvitationRequestSchema,
    SignupAndAcceptInvitationResponseSchema,
)
from src.modules.workforce.presentation.schemas.rbac.rbac_role_schemas import (
    CreatedByUserSchema,
)
from src.modules.workforce.workforce_container import (
    get_workforce_container,
    get_workforce_container_for_invitation_resolution,
)
from src.shared.dependencies.access_guard import require_access
from src.shared.dependencies.role_guard import require_org_role
from src.shared.infrastructure.db import get_async_session

# Managing invitations is a privileged action, restricted to management roles.
_MANAGER_ROLES = {"owner", "admin"}

# Admin endpoints — must be an org member with verified email and onboarding
admin_router = APIRouter(
    dependencies=[
        Depends(
            require_access(
                authenticated=True,
                email_verified=True,
                onboarded=True,
                organization_member=True,
            )
        )
    ]
)

# Authenticated user endpoints (accepting an invite) — NOT org-scoped because
# the user is being added to an org they aren't part of yet.
authenticated_router = APIRouter(
    dependencies=[
        Depends(
            require_access(
                authenticated=True,
                email_verified=True,
                onboarded=True,
            )
        )
    ]
)

# Public endpoints (preview by token) — anyone with the token may view.
public_router = APIRouter()

router = APIRouter()
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]


def _serialize_invitation(invitation, invited_by_user=None) -> dict:
    invited_by = (
        CreatedByUserSchema.model_validate(invited_by_user) if invited_by_user else None
    )
    return InvitationResponseSchema(
        uuid=invitation.uuid,
        email=invitation.email,
        status=invitation.status,
        role_id=invitation.role_id,
        team_id=invitation.team_id,
        expires_at=invitation.expires_at,
        accepted_at=invitation.accepted_at,
        created_at=invitation.created_at,
        invited_by=invited_by,
    ).model_dump()


# ---------------------- Admin endpoints ----------------------


@admin_router.post(
    "/invitations",
    response_model=CustomSuccessResponseSchema[InvitationResponseSchema],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_org_role(_MANAGER_ROLES))],
)
async def create_invitation(
    request: Request,
    body: CreateInvitationRequestSchema,
    session: AsyncSessionDep,
):
    """
    Issue a new invitation to join the organization. Returns the persisted
    invitation; the raw token is delivered out-of-band via email (the response
    does not include the token).
    """
    async with WorkforceUOW(session):
        container = get_workforce_container(session, request.state.organization_id)
        usecase: CreateInvitationUseCase = container.create_invitation_usecase()

        invitation, _raw_token = await usecase.execute(
            organization_id=request.state.organization_id,
            email=body.email,
            role_uuid=body.role_uuid,
            team_uuid=body.team_uuid,
            actor_id=request.state.user_id,
        )

        return cr.success(
            data=_serialize_invitation(invitation),
            message="Invitation sent successfully",
            status_code=status.HTTP_201_CREATED,
        )


@admin_router.get(
    "/invitations",
    response_model=CustomSuccessResponseSchema[list[InvitationResponseSchema]],
)
async def list_invitations(
    request: Request,
    session: AsyncSessionDep,
    invitation_status: Annotated[str | None, Query(alias="status")] = None,
):
    """
    List invitations for the current organization. Optional status filter.
    """
    async with WorkforceUOW(session):
        container = get_workforce_container(session, request.state.organization_id)
        usecase: ListInvitationsUseCase = container.list_invitations_usecase()

        invitations, users_by_id = await usecase.execute(status=invitation_status)
        payload = [
            _serialize_invitation(inv, users_by_id.get(inv.invited_by_id))
            for inv in invitations
        ]

        return cr.success(data=payload, message="Invitations listed successfully")


@admin_router.delete(
    "/invitations/{invitation_uuid}",
    response_model=CustomSuccessResponseSchema[None],
    dependencies=[Depends(require_org_role(_MANAGER_ROLES))],
)
async def revoke_invitation(
    request: Request,
    invitation_uuid: str,
    session: AsyncSessionDep,
):
    """
    Revoke a pending invitation.
    """
    async with WorkforceUOW(session):
        container = get_workforce_container(session, request.state.organization_id)
        usecase: RevokeInvitationUseCase = container.revoke_invitation_usecase()

        await usecase.execute(invitation_uuid)

        return cr.success(message="Invitation revoked successfully")


@admin_router.post(
    "/invitations/{invitation_uuid}/resend",
    response_model=CustomSuccessResponseSchema[InvitationResponseSchema],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_org_role(_MANAGER_ROLES))],
)
async def resend_invitation(
    request: Request,
    invitation_uuid: str,
    session: AsyncSessionDep,
):
    """
    Resend an invitation. The existing row is revoked and a fresh one with a
    new token + TTL is issued. The email is re-sent in the background.
    """
    async with WorkforceUOW(session):
        container = get_workforce_container(session, request.state.organization_id)
        usecase: ResendInvitationUseCase = container.resend_invitation_usecase()

        new_invitation, _raw_token = await usecase.execute(
            invitation_uuid=invitation_uuid,
            actor_id=request.state.user_id,
        )

        return cr.success(
            data=_serialize_invitation(new_invitation),
            message="Invitation resent successfully",
            status_code=status.HTTP_201_CREATED,
        )


# ---------------------- Public endpoint ----------------------


@public_router.get(
    "/invitations/token/{raw_token}",
    response_model=CustomSuccessResponseSchema[InvitationPreviewResponseSchema],
)
async def get_invitation_by_token(raw_token: str, session: AsyncSessionDep):
    """
    Public endpoint: resolve an invitation by raw token so the frontend can
    render a preview ("You've been invited to Acme as a member, accept?").
    No auth required — the token itself is the credential.
    """
    async with WorkforceUOW(session):
        container = get_workforce_container_for_invitation_resolution(session)
        usecase: GetInvitationByTokenUseCase = (
            container.get_invitation_by_token_usecase()
        )

        invitation, organization, role = await usecase.execute(raw_token)

        return cr.success(
            data=InvitationPreviewResponseSchema(
                email=invitation.email,
                organization_name=organization.name if organization else "",
                role_name=role.name if role else None,
                expires_at=invitation.expires_at,
            ).model_dump(),
            message="Invitation resolved",
        )


# ---------------------- Authenticated user endpoint ----------------------


@authenticated_router.post(
    "/invitations/token/{raw_token}/accept",
    response_model=CustomSuccessResponseSchema[AcceptInvitationResponseSchema],
    status_code=status.HTTP_201_CREATED,
)
async def accept_invitation(
    request: Request,
    raw_token: str,
    session: AsyncSessionDep,
):
    """
    Accept an invitation. The calling user MUST be logged in and their email
    must match the invitation email. The entire flow (membership creation,
    role assignment, optional team add, invitation status flip) runs in a
    single transaction.
    """
    async with WorkforceUOW(session):
        # The accepting user isn't yet a member of the inviting org, so we
        # can't use the org-scoped container until we know which org we're
        # joining. Resolve the invitation first via the org-less bootstrap
        # container, then build the proper org-scoped container.
        bootstrap_container = get_workforce_container_for_invitation_resolution(session)
        invitation_service = bootstrap_container.invitation_domain_service()
        invitation = await invitation_service.get_by_raw_token(raw_token)

        container = get_workforce_container(session, invitation.organization_id)
        usecase: AcceptInvitationUseCase = container.accept_invitation_usecase()

        accepting_user = request.state.user
        updated_invitation, membership = await usecase.execute(
            raw_token=raw_token,
            accepting_user_id=request.state.user_id,
            accepting_user_email=accepting_user.email,
        )

        organization = await bootstrap_container.organization_reader().get_organization(
            updated_invitation.organization_id
        )

        return cr.success(
            data=AcceptInvitationResponseSchema(
                invitation_uuid=updated_invitation.uuid,
                organization_uuid=organization.uuid if organization else "",
                organization_member_uuid=membership.uuid,
            ).model_dump(),
            message="Invitation accepted successfully",
            status_code=status.HTTP_201_CREATED,
        )


# ---------------------- Public signup-and-accept ----------------------


@public_router.post(
    "/invitations/token/{raw_token}/signup-and-accept",
    response_model=CustomSuccessResponseSchema[SignupAndAcceptInvitationResponseSchema],
    status_code=status.HTTP_201_CREATED,
)
async def signup_and_accept_invitation(
    raw_token: str,
    body: SignupAndAcceptInvitationRequestSchema,
    session: AsyncSessionDep,
):
    """
    Atomic flow for invited users who don't yet have an account.

    - Email is taken from the invitation, not the body — the user cannot
      register under a different email.
    - The new user lands email-verified and onboarded; no follow-up
      verification round-trip is required.
    - If an account already exists for the invited email, this endpoint
      returns 409 — the frontend should redirect the user to log in and
      use the regular `accept` endpoint instead.
    - On success the response sets the `session_uuid` cookie, so the user
      is immediately logged in.
    """
    async with WorkforceUOW(session):
        bootstrap_container = get_workforce_container_for_invitation_resolution(session)
        invitation_service = bootstrap_container.invitation_domain_service()
        invitation = await invitation_service.get_by_raw_token(raw_token)

        container = get_workforce_container(session, invitation.organization_id)
        usecase: SignupAndAcceptInvitationUseCase = (
            container.signup_and_accept_invitation_usecase()
        )

        updated_invitation, membership, provisioned = await usecase.execute(
            raw_token=raw_token,
            password=body.password,
            full_name=body.full_name,
        )

        organization = await bootstrap_container.organization_reader().get_organization(
            updated_invitation.organization_id
        )

        response = cr.success(
            data=SignupAndAcceptInvitationResponseSchema(
                invitation_uuid=updated_invitation.uuid,
                organization_uuid=organization.uuid if organization else "",
                organization_member_uuid=membership.uuid,
                user_uuid=provisioned.user_uuid,
                email=provisioned.email,
            ).model_dump(),
            message="Account created and invitation accepted successfully",
            status_code=status.HTTP_201_CREATED,
        )
        return get_cookie_response(
            cookies={"session_uuid": {"value": provisioned.session_uuid}},
            response=response,
        )


# ---------------------- Include ----------------------

router.include_router(admin_router)
router.include_router(authenticated_router)
router.include_router(public_router)
