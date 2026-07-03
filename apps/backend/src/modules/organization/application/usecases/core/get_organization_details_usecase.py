from src.modules.organization.domain.services.organization_domain_service import (
    OrganizationDomainService,
)
from src.modules.organization.domain.services.organization_media_domain_service import (
    OrganizationMediaDomainService,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class GetOrganizationDetailsUseCase:
    """
    Use case for getting organization details.
    """

    def __init__(
        self,
        organization_domain_service: OrganizationDomainService,
        organization_media_domain_service: OrganizationMediaDomainService,
    ):
        self.organization_domain_service = organization_domain_service
        self.organization_media_domain_service = organization_media_domain_service

    async def execute(self, organization_id: int):
        """
        Executes the use case to get organization details along with its media.
         - organization_id: The ID of the organization to retrieve details for.
        """
        try:
            organization = (
                await self.organization_domain_service.get_organization_by_id(
                    organization_id
                )
            )
            if not organization or not organization.id:
                raise ServerError(
                    error="Error while retrieving organization details",
                    internal_details=f"No organization found with ID {organization_id}",
                )

            media = await self.organization_media_domain_service.get_organization_media(
                organization_id=organization_id
            )

            return organization, media

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while retrieving organization details",
                internal_details=str(e),
            )
