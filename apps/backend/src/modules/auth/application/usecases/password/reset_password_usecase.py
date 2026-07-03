from src.modules.auth.application.usecases.session.revoke_all_user_sessions_usecase import (
    RevokeAllUserSessionsUseCase,
)
from src.modules.auth.domain.events.auth_password_domain_events import (
    PasswordChangedEvent,
)
from src.modules.auth.domain.services.user_account_domain_service import (
    UserAccountDomainService,
)
from src.shared.exceptions.base_exceptions import (
    DomainError,
    InvalidError,
    UpdateError,
)
from src.shared.infrastructure.hasher.hasher import HasherService
from src.shared.mediator.mediator import mediator


class ResetPasswordUseCase:
    """
    Use case for resetting a password while authenticated
    (user knows their current password and wants to set a new one).
    """

    def __init__(
        self,
        user_account_domain_service: UserAccountDomainService,
        revoke_all_user_sessions_usecase: RevokeAllUserSessionsUseCase,
        hasher: HasherService,
    ):
        self.user_account_domain_service = user_account_domain_service
        self.revoke_all_user_sessions_usecase = revoke_all_user_sessions_usecase
        self.hasher = hasher

    async def execute(
        self,
        user_id: int,
        old_password: str,
        new_password: str,
        except_session_uuid: str | None = None,
    ):
        """
        Executes the password reset process for an authenticated user.
        Verifies the old password before updating to the new one.
        Revokes all existing sessions on success.
        """
        try:
            account = (
                await self.user_account_domain_service.get_user_account_by_user_id(
                    user_id=user_id, type="credentials"
                )
            )

            if not account:
                raise InvalidError(error="User account not found")

            if not account.hashed_password or not account.is_credentials():
                raise InvalidError(error="User account is not of type credentials")

            if not self.hasher.verify(account.hashed_password, old_password):
                raise InvalidError(error="Invalid old password")

            account.change_password(self.hasher.hash(new_password))

            await self.user_account_domain_service.update_user_account(account)

            await self.revoke_all_user_sessions_usecase.execute(
                user_id=user_id, except_session_uuid=except_session_uuid
            )

            await mediator.publish(PasswordChangedEvent(user_id=user_id))

        except DomainError:
            raise
        except Exception as e:
            raise UpdateError(
                "Error while updating the password", internal_details=str(e)
            ) from e
