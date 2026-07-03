from datetime import UTC, datetime

from src.modules.organization.domain.ports.organization.organization_reader import (
    OrganizationReader,
)
from src.modules.workforce.domain.entities.invitation.invitation_entity import (
    InvitationEntity,
    InvitationStatus,
)
from src.modules.workforce.domain.services.invitation.invitation_domain_service import (
    InvitationDomainService,
)
from src.modules.workforce.domain.services.rbac.rbac_role_domain_service import (
    RbacRoleDomainService,
)
from src.shared.exceptions.base_exceptions import (
    DomainError,
    InvalidError,
    ServerError,
)


class GetInvitationByTokenUseCase:
    """
    Resolves an invitation by raw token for the public preview endpoint.

    Returns: (invitation, organization, role_name). Raises if revoked, expired,
    or otherwise unusable so that callers don't need to inspect status fields.
    """

    def __init__(
        self,
        invitation_domain_service: InvitationDomainService,
        organization_reader: OrganizationReader,
        rbac_role_domain_service: RbacRoleDomainService,
    ):
        self.invitation_domain_service = invitation_domain_service
        self.organization_reader = organization_reader
        self.rbac_role_domain_service = rbac_role_domain_service

    async def execute(self, raw_token: str):
        try:
            invitation: InvitationEntity = (
                await self.invitation_domain_service.get_by_raw_token(raw_token)
            )

            if invitation.is_revoked():
                raise InvalidError(error="Invitation has been revoked")
            if invitation.is_accepted():
                raise InvalidError(error="Invitation has already been accepted")
            if invitation.status == InvitationStatus.EXPIRED or invitation.is_expired(
                now=datetime.now(UTC)
            ):
                raise InvalidError(error="Invitation has expired")

            organization = await self.organization_reader.get_organization(
                invitation.organization_id
            )
            role = await self.rbac_role_domain_service.get_role_by_id(
                invitation.role_id
            )

            return invitation, organization, role
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to resolve invitation", internal_details=str(e)
            ) from e
