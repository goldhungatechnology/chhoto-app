from src.modules.auth.domain.events.auth_mfa_domain_events import (
    MFASetupCompletedEvent,
)
from src.modules.auth.domain.services.user_mfa_domain_service import (
    UserMFADomainService,
)
from src.modules.auth.domain.services.user_mfa_recovery_domain_service import (
    UserMFARecoveryDomainService,
)
from src.modules.auth.infrastructure.totp.totp_service import TOTPService
from src.shared.exceptions.base_exceptions import (
    DomainError,
    InvalidError,
    ServerError,
)
from src.shared.mediator.mediator import mediator


class ConfirmMFAUseCase:
    """
    Use case for confirming (enabling) MFA for a user.
    Verifies the TOTP code against the stored secret, marks MFA as verified,
    and generates emergency recovery codes.
    """

    def __init__(
        self,
        user_mfa_domain_service: UserMFADomainService,
        user_mfa_recovery_domain_service: UserMFARecoveryDomainService,
        totp_service: TOTPService,
    ):
        self.user_mfa_domain_service = user_mfa_domain_service
        self.user_mfa_recovery_domain_service = user_mfa_recovery_domain_service
        self.totp_service = totp_service

    async def execute(self, user_id: int, otp_code: str) -> dict:
        """
        Executes the use case to confirm MFA for the user.
        Returns verified status and generated recovery codes.
        """
        try:
            mfa = await self.user_mfa_domain_service.get_user_mfa_by_user_id(user_id)
            if not mfa:
                raise InvalidError(
                    error="MFA not set up. Please set up MFA first.",
                    errors={"mfa": "MFA not set up"},
                )

            if mfa.verified_at is not None:
                raise InvalidError(
                    error="MFA is already enabled.",
                    errors={"mfa": "MFA is already enabled"},
                )

            if not self.totp_service.verify_totp(mfa.secret, otp_code):
                raise InvalidError(
                    error="Invalid verification code. Please try again.",
                    errors={"otp_code": "Invalid verification code"},
                )

            confirmed_mfa = await self.user_mfa_domain_service.confirm_user_mfa(mfa)

            recovery_codes = await self.user_mfa_recovery_domain_service.create_recovery_codes_for_mfa(
                mfa_id=confirmed_mfa.id
            )

            await mediator.publish(MFASetupCompletedEvent(user_id=user_id))

            return {
                "verified": True,
                "recovery_codes": recovery_codes,
            }

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to confirm MFA", internal_details=str(e)
            ) from e
