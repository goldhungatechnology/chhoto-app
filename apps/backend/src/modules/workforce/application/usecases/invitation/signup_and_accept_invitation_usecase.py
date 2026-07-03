from src.modules.auth.domain.ports.user.user_provisioner import (
    ProvisionedUser,
    UserProvisioner,
)
from src.modules.organization.domain.ports.organization_member.organization_membership_writer import (
    OrganizationMembershipWriter,
)
from src.modules.workforce.domain.entities.rbac.rbac_member_role_entity import (
    MemberRoleEntity,
)
from src.modules.workforce.domain.entities.team.team_member_entity import (
    TeamMemberEntity,
    TeamMemberRole,
)
from src.modules.workforce.domain.events.invitation.invitation_domain_events import (
    InvitationAcceptedEvent,
)
from src.modules.workforce.domain.services.invitation.invitation_domain_service import (
    InvitationDomainService,
)
from src.modules.workforce.domain.services.rbac.rbac_member_role_domain_service import (
    RbacMemberRoleDomainService,
)
from src.modules.workforce.domain.services.team.team_member_domain_service import (
    TeamMemberDomainService,
)
from src.shared.exceptions.base_exceptions import (
    ConflictError,
    DomainError,
    ServerError,
)
from src.shared.mediator.mediator import mediator


class SignupAndAcceptInvitationUseCase:
    """
    Atomic flow for the common case where the invitee has no account yet.

    Behavior:
      - resolves the invitation by raw token
      - validates lifecycle (revoked / expired / accepted / pending) — email
        match is implicit because the user we provision uses the invitation's
        email
      - if a user with the invitation email already exists, raises
        ConflictError (frontend should redirect to log in → accept)
      - provisions the user with email pre-verified and onboarding skipped
      - creates organization membership, role assignment, optional team add
      - marks invitation accepted

    Everything runs in the caller's transaction (router-level UoW). Any
    failure rolls back the whole flow — no orphan users, no half-joined
    members.
    """

    def __init__(
        self,
        invitation_domain_service: InvitationDomainService,
        user_provisioner: UserProvisioner,
        organization_membership_writer: OrganizationMembershipWriter,
        rbac_member_role_domain_service: RbacMemberRoleDomainService,
        team_member_domain_service: TeamMemberDomainService,
    ):
        self.invitation_domain_service = invitation_domain_service
        self.user_provisioner = user_provisioner
        self.organization_membership_writer = organization_membership_writer
        self.rbac_member_role_domain_service = rbac_member_role_domain_service
        self.team_member_domain_service = team_member_domain_service

    async def execute(
        self,
        *,
        raw_token: str,
        password: str,
        full_name: str | None,
    ):
        try:
            invitation = await self.invitation_domain_service.get_by_raw_token(
                raw_token
            )

            # Lifecycle validation. Email match is enforced by construction:
            # we're about to provision a user whose email equals
            # `invitation.email`.
            self.invitation_domain_service.ensure_acceptable(
                invitation, accepting_email=invitation.email
            )

            # Provision the user. The provisioner enforces email uniqueness;
            # a ConflictError here means the account already exists and the
            # caller should switch to the log-in-then-accept flow.
            try:
                provisioned: ProvisionedUser = (
                    await self.user_provisioner.provision_invited_user(
                        email=invitation.email,
                        password=password,
                        full_name=full_name,
                    )
                )
            except ConflictError as e:
                raise ConflictError(
                    error=(
                        "An account already exists for this email. "
                        "Please log in and use the standard accept flow."
                    ),
                    internal_details=str(e),
                ) from e

            membership = await self.organization_membership_writer.create_membership(
                organization_id=invitation.organization_id,
                user_id=provisioned.user_id,
                actor_id=provisioned.user_id,
            )
            if not membership.id:
                raise ServerError(error="Failed to create organization membership")

            member_role = MemberRoleEntity(
                member_id=membership.id,
                role_id=invitation.role_id,
                created_by_id=provisioned.user_id,
            )
            created_member_role = (
                await self.rbac_member_role_domain_service.create_member_role(
                    member_role
                )
            )
            for event in created_member_role.pull_events():
                await mediator.publish(event)

            if invitation.team_id is not None:
                team_member = TeamMemberEntity(
                    team_id=invitation.team_id,
                    member_id=membership.id,
                    role=TeamMemberRole.MEMBER,
                    created_by_id=provisioned.user_id,
                )
                created_team_member = (
                    await self.team_member_domain_service.add_team_member(
                        team_member, organization_id=invitation.organization_id
                    )
                )
                for event in created_team_member.pull_events():
                    await mediator.publish(event)

            updated_invitation = await self.invitation_domain_service.mark_as_accepted(
                invitation
            )

            if updated_invitation.id:
                await mediator.publish(
                    InvitationAcceptedEvent(
                        invitation_id=updated_invitation.id,
                        organization_id=updated_invitation.organization_id,
                        user_id=provisioned.user_id,
                        organization_member_id=membership.id,
                    )
                )

            return updated_invitation, membership, provisioned
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to sign up and accept invitation",
                internal_details=str(e),
            ) from e
