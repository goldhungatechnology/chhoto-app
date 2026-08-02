from src.core.config.settings import config
from src.modules.auth.domain.entities.user_session_entity import UserSessionEntity
from src.modules.auth.domain.services.user_mfa_domain_service import (
    UserMFADomainService,
)
from src.modules.auth.domain.services.user_mfa_recovery_domain_service import (
    UserMFARecoveryDomainService,
)
from src.modules.auth.domain.services.user_session_domain_service import (
    UserSessionDomainService,
)
from src.modules.auth.infrastructure.totp.totp_service import TOTPService
from src.shared.exceptions.base_exceptions import (
    DomainError,
    InvalidError,
    ServerError,
)
from src.shared.infrastructure.token.token_service import TokenService


class VerifyMFAUseCase:
    """
    Use case for verifying an MFA code during login.
    Validates the temp_token, verifies the TOTP code or a single-use recovery
    code, and creates a session.
    """

    def __init__(
        self,
        user_mfa_domain_service: UserMFADomainService,
        user_mfa_recovery_domain_service: UserMFARecoveryDomainService,
        user_session_domain_service: UserSessionDomainService,
        totp_service: TOTPService,
        token_service: TokenService,
    ):
        self.user_mfa_domain_service = user_mfa_domain_service
        self.user_mfa_recovery_domain_service = user_mfa_recovery_domain_service
        self.user_session_domain_service = user_session_domain_service
        self.totp_service = totp_service
        self.token_service = token_service

    async def execute(
        self,
        temp_token: str,
        otp_code: str | None = None,
        recovery_code: str | None = None,
        ip_address: str = "",
        device: str = "",
        browser: str = "",
    ) -> dict:
        """
        Executes the use case to verify MFA code during login.
        """
        try:
            payload = self.token_service.validate_token(temp_token)

            token_type = payload.get("type")
            if token_type != "mfa":
                raise InvalidError(
                    error="Invalid token type",
                    errors={"temp_token": "Invalid token"},
                )

            user_id = payload.get("user_id")
            if not isinstance(user_id, int):
                raise InvalidError(
                    error="Invalid token payload",
                    errors={"temp_token": "Invalid token"},
                )

            mfa = await self.user_mfa_domain_service.get_verified_user_mfa_by_user_id(
                user_id
            )
            if not mfa:
                raise InvalidError(
                    error="MFA is not enabled for this user.",
                    errors={"mfa": "MFA not enabled"},
                )

            await self._verify_credentials(mfa, otp_code, recovery_code)

            session_entity = UserSessionEntity(
                user_id=user_id,
                expires_at=UserSessionEntity.set_expiration(),
                ip_address=ip_address,
                device=device,
                browser=browser,
            )

            total_sessions = (
                await self.user_session_domain_service.list_sessions_by_user_id(user_id)
            )
            if len(total_sessions) >= config.MAX_AUTH_CONCURRENT_SESSIONS:
                raise InvalidError(
                    error=f"Maximum concurrent sessions exceeded. You have {len(total_sessions)} active sessions.",
                )

            created_session = (
                await self.user_session_domain_service.create_user_session(
                    session_entity
                )
            )

            return {
                "session_uuid": created_session.uuid,
            }

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to verify MFA code", internal_details=str(e)
            ) from e

    async def _verify_credentials(
        self,
        mfa,
        otp_code: str | None,
        recovery_code: str | None,
    ) -> None:
        """
        Validates the provided MFA credential. Exactly one of otp_code or
        recovery_code must be present.
        """
        if recovery_code:
            recovery_verified = (
                await self.user_mfa_recovery_domain_service.verify_recovery_code(
                    mfa_id=mfa.id, plain_code=recovery_code
                )
            )
            if not recovery_verified:
                raise InvalidError(
                    error="Invalid recovery code. Please try again.",
                    errors={"recovery_code": "Invalid recovery code"},
                )
            return

        if not otp_code:
            raise InvalidError(
                error="Provide either a TOTP code or a recovery code.",
                errors={"otp_code": "Missing MFA code"},
            )

        if not self.totp_service.verify_totp(mfa.secret, otp_code):
            raise InvalidError(
                error="Invalid MFA code. Please try again.",
                errors={"otp_code": "Invalid MFA code"},
            )
