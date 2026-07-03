from src.core.config.settings import config
from src.modules.auth.domain.events.auth_password_domain_events import (
    ForgotPasswordLinkCreatedEvent,
)
from src.modules.auth.domain.services.user_domain_service import UserDomainService
from src.modules.auth.domain.services.user_token_domain_service import (
    UserTokenDomainService,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError
from src.shared.mediator.mediator import mediator


class ForgotPasswordUseCase:
    """
    Use case for handling the forgot password process.
    """

    def __init__(
        self,
        user_domain_service: UserDomainService,
        user_token_domain_service: UserTokenDomainService,
    ):
        self.user_domain_service = user_domain_service
        self.user_token_domain_service = user_token_domain_service

    async def execute(self, email: str):
        """
        Executes the forgot password process.
        """

        try:
            user = await self.user_domain_service.get_user_by_email(email=email)
            if not user or not user.id:
                return None  ## To prevent email enumeration, we return early if the user is not found without raising an error. To confuse attackers who might be trying to guess valid email addresses, we simply exit the function without any indication of whether the email exists or not.

            # Invalidate any previously-issued reset links so only the newest
            # one is ever valid (prevents multiple concurrently-live tokens).
            await self.user_token_domain_service.invalidate_active_tokens(
                user_id=user.id, type="forgot-password"
            )

            token = await self.user_token_domain_service.create_user_token(
                user_id=user.id,
                type="forgot-password",
                expiry_minutes=config.FORGOT_PASSWORD_TOKEN_EXPIRE_MINUTES,
            )

            forgot_password_link = await self._generate_forgot_password_link(token)

            user.add_event(
                ForgotPasswordLinkCreatedEvent(
                    email=user.email,
                    link=forgot_password_link,
                )
            )

            ## publishing the events
            for event in user.pull_events():
                await mediator.publish(event)

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to process forgot password request",
                internal_details=str(e),
            ) from e

    async def _generate_forgot_password_link(self, token: str) -> str:
        """
        Generates the forgot password link to be sent to the user.
        """
        path = "auth/set-password"
        return f"{config.FRONTEND_URL}/{path}?token={token}"
