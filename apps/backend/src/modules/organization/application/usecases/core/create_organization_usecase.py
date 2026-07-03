from src.modules.organization.domain.entities.organization_entity import (
    OrganizationEntity,
)
from src.modules.organization.domain.entities.organization_member_entity import (
    OrganizationMemberEntity,
)
from src.modules.organization.domain.entities.organization_onboarding_entity import (
    OrganizationOnboardingEntity,
)
from src.modules.organization.domain.events.organization_domain_events import (
    OrganizationActivatedEvent,
    OrganizationCreatedEvent,
)
from src.modules.organization.domain.services.organization_domain_service import (
    OrganizationDomainService,
)
from src.modules.organization.domain.services.organization_member_domain_service import (
    OrganizationMemberDomainService,
)
from src.modules.organization.domain.services.organization_onboarding_domain_service import (
    OrganizationOnboardingDomainService,
)
from src.modules.organization.presentation.schemas.organization_schemas import (
    CreateOrganizationRequestSchema,
)
from src.shared.exceptions.base_exceptions import CreateError, DomainError, ServerError
from src.shared.mediator.mediator import mediator


class CreateOrganizationUseCase:
    """
    Use case for creating an organization and adding its owner as member.
    """

    def __init__(
        self,
        organization_domain_service: OrganizationDomainService,
        organization_member_domain_service: OrganizationMemberDomainService,
        organization_onboarding_domain_service: OrganizationOnboardingDomainService,
    ):
        self.organization_domain_service = organization_domain_service
        self.organization_member_domain_service = organization_member_domain_service
        self.organization_onboarding_domain_service = (
            organization_onboarding_domain_service
        )

    async def execute(
        self, payload: CreateOrganizationRequestSchema, actor_id: int
    ) -> dict[str, str]:
        """
        execute the use case to create an organization and add its owner as member.
        """
        try:
            organization = OrganizationEntity(
                name=payload.name,
                description=payload.description,
                type="external",
                slug=self._get_slug_from_name(payload.name),
                status="pending",  ## After all setup is complete it will be set active, this is to prevent the organization from being used before setup is complete
                logo=payload.logo,
                domain=payload.domain,
                owner_id=actor_id,
                created_by_id=actor_id,
            )
            created_organization = (
                await self.organization_domain_service.create_organization(organization)
            )
            if not created_organization.id:
                raise CreateError(error="Failed to create organization")

            _ = await self._handle_organization_onboarding(
                payload, created_organization.id
            )
            org_member = await self._handle_organization_membership(
                created_organization.id, actor_id
            )

            if not org_member.id:
                raise CreateError(
                    error="Failed to create organization",
                    internal_details="Failed to create organization membership for the owner",
                )

            # Phase 1: inline must-succeed provisioning. Any listener failure
            # here propagates and the router's UoW rolls back the whole
            # organization creation. Org status stays "pending" only if we
            # never reach activation below.
            await mediator.publish(
                OrganizationCreatedEvent(
                    actor_id=actor_id,
                    organization_id=created_organization.id,
                    organization_member_id=org_member.id,
                    session=self.organization_domain_service.repository.session,
                ),
                raise_on_error=True,
            )

            # Phase 2: activate the organization in the SAME transaction once
            # all provisioning listeners have committed their writes.
            await self.organization_domain_service.activate_organization(
                created_organization.id
            )

            # Phase 3: fire-and-forget follow-ups (welcome email, analytics,
            # billing customer, etc.). Listeners on this event MUST be
            # background-task wrappers — failures here do not roll back.
            await mediator.publish(
                OrganizationActivatedEvent(
                    actor_id=actor_id,
                    organization_id=created_organization.id,
                    organization_member_id=org_member.id,
                )
            )

            return {
                "organization_uuid": created_organization.uuid,
                "organization_slug": created_organization.slug,
            }
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while creating organization",
                internal_details=str(e),
            ) from e

    def _get_slug_from_name(self, name: str) -> str:
        """
        Generate a slug from the organization name.
        """
        return name.strip().lower().replace(" ", "-")

    async def _handle_organization_onboarding(
        self, payload: CreateOrganizationRequestSchema, organization_id: int
    ) -> OrganizationOnboardingEntity:
        """
        Handle the organization onboarding process.
        """

        organization_onboarding = OrganizationOnboardingEntity(
            organization_id=organization_id,
            size_range=payload.onboarding.size_range,
            use_case=payload.onboarding.use_case,
            industry=payload.onboarding.industry,
            previous_tool=payload.onboarding.previous_tool,
        )

        try:
            created_onboarding = await self.organization_onboarding_domain_service.create_organization_onboarding(
                organization_onboarding
            )
            return created_onboarding
        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to create organization onboarding",
                internal_details=str(e),
            ) from e

    async def _handle_organization_membership(
        self, organization_id: int, user_id: int
    ) -> OrganizationMemberEntity:
        """
        Handle the organization membership creation for the owner.
        """

        membership = OrganizationMemberEntity(
            organization_id=organization_id,
            user_id=user_id,
            status="active",
            created_by_id=user_id,
        )

        try:
            created_membership = (
                await self.organization_member_domain_service.add_member(membership)
            )
            return created_membership
        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to create organization membership",
                internal_details=str(e),
            ) from e
