from src.modules.auth.domain.services.user_domain_service import UserDomainService
from src.modules.auth.domain.services.user_token_domain_service import (
    UserTokenDomainService,
)
from src.shared.exceptions.base_exceptions import DomainError, InvalidError, ServerError
from src.shared.mediator.mediator import mediator


class EmailVerificationUseCase:
    """
    Use case for verifying a user's email address.
    """

    def __init__(
        self,
        user_domain_service: UserDomainService,
        user_token_domain_service: UserTokenDomainService,
    ):
        self.user_domain_service = user_domain_service
        self.user_token_domain_service = user_token_domain_service

    async def execute(self, user_id: int, token: str):
        """
        Executes the use case to verify a user's email address.

        1. Verifies the provided token for the user.
        2. If the token is valid, updates the user's email_verified status to True.
        3. Marks the token as used to prevent reuse.
        4. Returns True if the email was successfully verified, otherwise False.
        """
        try:
            (
                is_valid_token,
                user_token,
            ) = await self.user_token_domain_service.verify_user_token(
                type="email_verification", user_id=user_id, token=token
            )
            if not is_valid_token or not user_token:
                raise InvalidError(
                    error="Invalid or expired token",
                    errors={"token": "Invalid or expired token"},
                )

            updated_user = await self.user_domain_service.mark_email_verified(
                user_id=user_id
            )
            await self.user_token_domain_service.mark_token_as_used(user_token)

            ## Emitting events
            for event in updated_user.pull_events():
                await mediator.publish(event)

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to verify email", internal_details=str(e)
            ) from e
