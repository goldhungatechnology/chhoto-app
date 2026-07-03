from src.modules.auth.application.usecases.session.revoke_all_user_sessions_usecase import (
    RevokeAllUserSessionsUseCase,
)
from src.modules.auth.domain.events.auth_password_domain_events import (
    PasswordChangedEvent,
)
from src.modules.auth.domain.services.user_account_domain_service import (
    UserAccountDomainService,
)
from src.modules.auth.domain.services.user_domain_service import UserDomainService
from src.modules.auth.domain.services.user_token_domain_service import (
    UserTokenDomainService,
)
from src.shared.exceptions.base_exceptions import (
    DomainError,
    InvalidError,
    ServerError,
    UpdateError,
)
from src.shared.infrastructure.hasher.hasher import HasherService
from src.shared.mediator.mediator import mediator


class VerifyForgotPasswordUseCase:
    """
    Use case for verifying a forgot password request.
    """

    def __init__(
        self,
        user_domain_service: UserDomainService,
        user_account_domain_service: UserAccountDomainService,
        user_token_domain_service: UserTokenDomainService,
        revoke_all_user_sessions_usecase: RevokeAllUserSessionsUseCase,
        hasher: HasherService,
    ):
        self.user_domain_service = user_domain_service
        self.user_account_domain_service = user_account_domain_service
        self.user_token_domain_service = user_token_domain_service
        self.revoke_all_user_sessions_usecase = revoke_all_user_sessions_usecase
        self.hasher = hasher

    async def execute(self, token: str, new_password: str):
        """
        Executes the forgot password verification process.

        The emailed token is the sole proof of identity for a user who has
        forgotten their password, so we MUST NOT demand the old password here.
        On success the token is consumed so it cannot be reused.
        """
        try:
            user_token = await self.user_token_domain_service.get_user_token_by_token(
                token=token, type="forgot-password"
            )

            if not user_token or not user_token.user_id:
                raise InvalidError(error="Invalid or expired token")

            user = await self.user_domain_service.get_user_by_id(
                user_id=user_token.user_id
            )
            if not user or not user.id:
                raise InvalidError(
                    error="Invalid or expired token",
                    internal_details="User not found for the provided token",
                )

            await self._handle_password_change(user, new_password)

            # Consume the token so the reset link is single-use.
            await self.user_token_domain_service.mark_token_as_used(user_token)

            # Revoke all existing sessions: a password reset must lock out any
            # attacker who may already hold a hijacked session for this user.
            await self.revoke_all_user_sessions_usecase.execute(user_id=user.id)

            await mediator.publish(PasswordChangedEvent(user_id=user.id))

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to verify forgot password request",
                internal_details=str(e),
            ) from e

    async def _handle_password_change(self, user, new_password):
        """
        Handles the password change process after token verification.
        """
        try:
            account = (
                await self.user_account_domain_service.get_user_account_by_user_id(
                    user_id=user.id, type="credentials"
                )
            )
            if not account:
                raise InvalidError(error="User account not found")

            if not account.hashed_password or not account.is_credentials():
                raise InvalidError(
                    error="User account is not of type credentials, You have to first setup your password"
                )

            account.change_password(self.hasher.hash(new_password))

            await self.user_account_domain_service.update_user_account(account)
        except DomainError:
            raise
        except Exception as e:
            raise UpdateError(
                "Error while updating the new password", internal_details=str(e)
            ) from e
