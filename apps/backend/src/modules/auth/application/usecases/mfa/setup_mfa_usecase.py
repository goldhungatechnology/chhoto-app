from src.modules.auth.domain.entities.user_mfa_entity import UserMFAEntity
from src.modules.auth.domain.services.user_domain_service import UserDomainService
from src.modules.auth.domain.services.user_mfa_domain_service import (
    UserMFADomainService,
)
from src.modules.auth.infrastructure.totp.totp_service import TOTPService
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class SetupMFAUseCase:
    """
    Use case for setting up MFA for a user.
    Generates a TOTP secret and auth URL, creates an unverified MFA record.
    """

    def __init__(
        self,
        user_domain_service: UserDomainService,
        user_mfa_domain_service: UserMFADomainService,
        totp_service: TOTPService,
    ):
        self.user_domain_service = user_domain_service
        self.user_mfa_domain_service = user_mfa_domain_service
        self.totp_service = totp_service

    async def execute(self, user_id: int) -> dict:
        """
        Executes the use case to set up MFA for the user.
        """
        try:
            user = await self.user_domain_service.get_user_by_id(user_id)
            if not user or not user.id:
                raise DomainError(error="User not found")

            secret = self.totp_service.generate_secret()
            auth_url = self.totp_service.generate_auth_url(
                secret=secret, email=user.email
            )

            mfa_entity = UserMFAEntity(
                user_id=user.id,
                secret=secret,
                method="TOTP",
                auth_url=auth_url,
            )

            created_mfa = await self.user_mfa_domain_service.create_user_mfa(mfa_entity)

            return {
                "secret": created_mfa.secret,
                "auth_url": created_mfa.auth_url,
            }

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to set up MFA", internal_details=str(e)
            ) from e
