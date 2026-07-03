from src.modules.auth.domain.services.user_account_domain_service import (
    UserAccountDomainService,
)
from src.modules.auth.domain.services.user_domain_service import UserDomainService
from src.modules.auth.domain.services.user_mfa_domain_service import (
    UserMFADomainService,
)
from src.modules.auth.domain.services.user_onboarding_domain_service import (
    UserOnboardingDomainService,
)
from src.modules.auth.domain.services.user_session_domain_service import (
    UserSessionDomainService,
)
from src.modules.auth.infrastructure.cache.auth_cache_service import AuthCacheService
from src.shared.exceptions.base_exceptions import DomainError, InvalidError, ServerError
from src.shared.infrastructure.country.country_reader import CountryReader
from src.modules.organization.domain.ports.organization.organization_reader import (
    OrganizationReader,
)


class GetUserDetailsUseCase:
    """
    Use case for retrieving user details by user ID.
    """

    def __init__(
        self,
        user_domain_service: UserDomainService,
        user_onboarding_domain_service: UserOnboardingDomainService,
        user_account_domain_service: UserAccountDomainService,
        organization_reader: OrganizationReader,
        user_session_domain_service: UserSessionDomainService,
        cache_service: AuthCacheService,
        country_reader: CountryReader,
        user_mfa_domain_service: UserMFADomainService,
    ):
        self.user_domain_service = user_domain_service
        self.user_session_domain_service = user_session_domain_service
        self.user_account_domain_service = user_account_domain_service
        self.user_onboarding_domain_service = user_onboarding_domain_service
        self.organization_reader = organization_reader
        self.cache_service = cache_service
        self.country_reader = country_reader
        self.user_mfa_domain_service = user_mfa_domain_service

    async def execute(self, user_id: int, session_uuid: str):
        """
        Executes the use case to retrieve user details by user ID.
        """
        try:
            user = await self.user_domain_service.get_user_by_id(user_id)
            if not user or not user.id:
                raise ServerError(
                    error="Error while retrieving user details",
                    internal_details=f"No user found with ID {user_id}",
                )

            user_account = (
                await self.user_account_domain_service.get_user_account_by_user_id(
                    user_id=user.id, type="credentials"
                )
            )

            organizations = await self.organization_reader.get_organizations_by_user_id(
                user.id
            )
            last_organization = organizations[0] if organizations else None

            current_session = (
                await self.user_session_domain_service.get_user_session_by_uuid(
                    session_uuid
                )
            )
            if current_session and current_session.organization_uuid:
                last_organization = (
                    await self.organization_reader.get_organization_by_uuid(
                        current_session.organization_uuid
                    )
                )

            onboarding_details = await self.user_onboarding_domain_service.get_user_onboarding_by_user_id(
                user.id
            )
            if not organizations:
                raise InvalidError(
                    error="Error while retrieving user details",
                    errors={"code": "ORGANIZATION_NOT_FOUND"},
                    internal_details=f"No organizations found for user ID {user_id}",
                )

            is_online = await self.cache_service.is_user_online(user_id)

            country = (
                await self.country_reader.get_country_by_id(user.country_id)
                if user.country_id
                else None
            )

            mfa_enabled = await self.user_mfa_domain_service.is_mfa_required(user_id)

            return (
                user,
                onboarding_details,
                organizations,
                is_online,
                last_organization,
                country,
                user_account,
                mfa_enabled,
            )

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while retrieving user details",
                internal_details=str(e),
            ) from e
