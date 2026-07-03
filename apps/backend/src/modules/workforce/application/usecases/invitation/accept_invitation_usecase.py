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
    CreateError,
    DomainError,
    ServerError,
)
from src.shared.mediator.mediator import mediator


class AcceptInvitationUseCase:
    """
    Accept an invitation. Logged-in user only. All writes happen in the
    caller's transaction (router-level UoW) so a failure anywhere reverts the
    whole acceptance — no half-joined members, no orphan role assignments.

    Sequence:
      1. resolve invitation by raw token
      2. validate (status, expiry, email-match against the calling user)
      3. create organization membership
      4. assign the invitation's role to the new membership
      5. if invitation has team_id, add to team (best-effort: skipped silently
         if the team was deleted since the invitation was issued)
      6. mark invitation accepted
      7. publish InvitationAcceptedEvent
    """

    def __init__(
        self,
        invitation_domain_service: InvitationDomainService,
        organization_membership_writer: OrganizationMembershipWriter,
        rbac_member_role_domain_service: RbacMemberRoleDomainService,
        team_member_domain_service: TeamMemberDomainService,
    ):
        self.invitation_domain_service = invitation_domain_service
        self.organization_membership_writer = organization_membership_writer
        self.rbac_member_role_domain_service = rbac_member_role_domain_service
        self.team_member_domain_service = team_member_domain_service

    async def execute(
        self,
        *,
        raw_token: str,
        accepting_user_id: int,
        accepting_user_email: str,
    ):
        try:
            invitation = await self.invitation_domain_service.get_by_raw_token(
                raw_token
            )
            self.invitation_domain_service.ensure_acceptable(
                invitation, accepting_email=accepting_user_email
            )

            membership = await self.organization_membership_writer.create_membership(
                organization_id=invitation.organization_id,
                user_id=accepting_user_id,
                actor_id=accepting_user_id,
            )
            if not membership.id:
                raise CreateError(error="Failed to create organization membership")

            member_role = MemberRoleEntity(
                member_id=membership.id,
                role_id=invitation.role_id,
                created_by_id=accepting_user_id,
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
                    created_by_id=accepting_user_id,
                )
                created_team_member = (
                    await self.team_member_domain_service.add_team_member(
                        team_member, organization_id=invitation.organization_id
                    )
                )
                for event in created_team_member.pull_events():
                    await mediator.publish(event)

            updated = await self.invitation_domain_service.mark_as_accepted(invitation)

            if updated.id:
                await mediator.publish(
                    InvitationAcceptedEvent(
                        invitation_id=updated.id,
                        organization_id=updated.organization_id,
                        user_id=accepting_user_id,
                        organization_member_id=membership.id,
                    )
                )

            return updated, membership
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to accept invitation", internal_details=str(e)
            ) from e
