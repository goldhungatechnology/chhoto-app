from src.core.config.settings import config
from src.modules.auth.domain.events.auth_email_domain_events import (
    ResendEmailVerificationTokenEvent,
)
from src.modules.auth.domain.services.user_domain_service import UserDomainService
from src.modules.auth.domain.services.user_token_domain_service import (
    UserTokenDomainService,
)
from src.shared.exceptions.base_exceptions import (
    ConflictError,
    DomainError,
    InvalidError,
    ServerError,
)
from src.shared.mediator.mediator import mediator


class EmailVerificationResendUseCase:
    """
    Use case for resending email verification token.
    """

    def __init__(
        self,
        user_domain_service: UserDomainService,
        user_token_domain_service: UserTokenDomainService,
    ):
        self.user_domain_service = user_domain_service
        self.user_token_domain_service = user_token_domain_service

    async def execute(self, user_id: int) -> str:
        """
        Executes the use case to resend email verification token.

        1. Checks if the user's email is already verified. If it is, raises an error.
        2. If the email is not verified, creates a new email verification token for the user.
        3. Returns the newly created token.
        """
        try:
            user = await self.user_domain_service.get_user_by_id(user_id)
            if not user:
                raise InvalidError("User not found")
            if user.is_email_verified():
                raise ConflictError("Email is already verified")

            prev_tokens = await self.user_token_domain_service.list_user_tokens(
                user_id=user_id, type="email_verification"
            )

            ## deactivating previous tokens
            for token in prev_tokens:
                await self.user_token_domain_service.mark_token_as_used(token)

            new_token = await self.user_token_domain_service.create_user_token(
                user_id=user_id,
                type="email_verification",
                expiry_minutes=config.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES,
            )

            await mediator.publish(
                ResendEmailVerificationTokenEvent(
                    username=user.username,
                    email=user.email,
                    token=new_token,
                )
            )

            return new_token
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to resend email verification token",
                internal_details=str(e),
            ) from e
