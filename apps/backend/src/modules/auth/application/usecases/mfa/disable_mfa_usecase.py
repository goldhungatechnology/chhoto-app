from src.modules.auth.domain.events.auth_mfa_domain_events import MFADisabledEvent
from src.modules.auth.domain.services.user_account_domain_service import (
    UserAccountDomainService,
)
from src.modules.auth.domain.services.user_mfa_domain_service import (
    UserMFADomainService,
)
from src.shared.exceptions.base_exceptions import (
    DomainError,
    InvalidError,
    ServerError,
)
from src.shared.infrastructure.hasher.hasher import HasherService
from src.shared.mediator.mediator import mediator


class DisableMFAUseCase:
    """
    Use case for disabling MFA for a user.
    Verifies the user's password and revokes the MFA record.
    """

    def __init__(
        self,
        user_mfa_domain_service: UserMFADomainService,
        user_account_domain_service: UserAccountDomainService,
        hasher_service: HasherService,
    ):
        self.user_mfa_domain_service = user_mfa_domain_service
        self.user_account_domain_service = user_account_domain_service
        self.hasher_service = hasher_service

    async def execute(self, user_id: int, password: str) -> dict:
        """
        Executes the use case to disable MFA for the user.
        """
        try:
            mfa = await self.user_mfa_domain_service.get_user_mfa_by_user_id(user_id)
            if not mfa:
                raise InvalidError(
                    error="MFA is not enabled.",
                    errors={"mfa": "MFA is not enabled"},
                )

            account = (
                await self.user_account_domain_service.get_user_account_by_user_id(
                    user_id=user_id, type="credentials"
                )
            )
            if not account or not account.hashed_password:
                raise InvalidError(
                    error="User account not found",
                    errors={"password": "User account not found"},
                )

            if not self.hasher_service.verify(account.hashed_password, password):
                raise InvalidError(
                    error="Invalid password",
                    errors={"password": "Invalid password"},
                )

            await self.user_mfa_domain_service.disable_user_mfa(mfa)

            await mediator.publish(MFADisabledEvent(user_id=user_id))

            return {"disabled": True}

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to disable MFA", internal_details=str(e)
            ) from e
