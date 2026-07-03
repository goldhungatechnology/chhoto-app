from src.modules.organization.domain.entities.organization_entity import (
    OrganizationEntity,
)
from src.modules.organization.domain.services.organization_domain_service import (
    OrganizationDomainService,
)
from src.shared.mediator.mediator import mediator


class SwitchOrganizationUseCase:
    """
    Use case for switching the current organization of the user.
     - This use case will update the user's current organization in the database and return the updated user information.
    """

    def __init__(self, organization_domain_service: OrganizationDomainService):
        self.organization_domain_service = organization_domain_service

    async def execute(
        self, user_id: int, target_organization_uuid: str, current_session_uuid: str
    ) -> OrganizationEntity:
        """
        Executes the use case to switch the user's current organization.
        """

        organization = await self.organization_domain_service.switch_organization(
            user_id=user_id,
            target_organization_uuid=target_organization_uuid,
            current_session_uuid=current_session_uuid,
        )

        for event in organization.pull_events():
            await mediator.publish(event)

        return organization
