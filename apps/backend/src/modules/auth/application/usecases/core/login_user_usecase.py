from datetime import UTC, datetime
from typing import Any

from src.core.config.settings import config
from src.modules.auth.domain.entities.user_session_entity import UserSessionEntity
from src.modules.auth.domain.events.auth_domain_events import (
    UserInvalidLoginAttemptEvent,
)
from src.modules.auth.domain.services.user_account_domain_service import (
    UserAccountDomainService,
)
from src.modules.auth.domain.services.user_domain_service import UserDomainService
from src.modules.auth.domain.services.user_mfa_domain_service import (
    UserMFADomainService,
)
from src.modules.auth.domain.services.user_session_domain_service import (
    UserSessionDomainService,
)
from src.shared.exceptions.base_exceptions import DomainError, InvalidError, ServerError
from src.shared.infrastructure.captcha import captcha
from src.shared.infrastructure.hasher.hasher import HasherService
from src.shared.infrastructure.token.token_service import TokenService
from src.shared.mediator.mediator import mediator


class LoginUserUseCase:
    """
    Use case for logging in a user.
    """

    def __init__(
        self,
        user_domain_service: UserDomainService,
        user_session_domain_service: UserSessionDomainService,
        user_account_domain_service: UserAccountDomainService,
        user_mfa_domain_service: UserMFADomainService,
        hasher_service: HasherService,
        token_service: TokenService,
    ):
        self.user_domain_service = user_domain_service
        self.user_account_domain_service = user_account_domain_service
        self.user_session_domain_service = user_session_domain_service
        self.user_mfa_domain_service = user_mfa_domain_service
        self.hasher_service = hasher_service
        self.token_service = token_service
        self.captcha = captcha

    async def execute(
        self,
        email: str,
        password: str,
        ip_address: str,
        device: str,
        browser: str,
        captcha_token: str | None,
    ) -> dict[str, Any]:
        """
        Executes the use case to log in a user.
        """
        user = None
        try:
            if config.ENABLE_CAPTCHA:
                if not captcha_token or not await self.captcha.verify(
                    token=captcha_token, ip=ip_address
                ):
                    raise InvalidError(
                        error="Captcha verification failed",
                        errors={"captcha_token": "Captcha verification failed"},
                    )

            user = await self.user_domain_service.get_user_by_email(email)
            if not user or not user.id:
                self.hasher_service.dummy_verify(password)
                raise InvalidError(
                    error="Invalid credentials", errors={"email": "Invalid credentials"}
                )

            user_account = (
                await self.user_account_domain_service.get_user_account_by_user_id(
                    user_id=user.id, type="credentials"
                )
            )

            if not user_account or not user_account.hashed_password:
                self.hasher_service.dummy_verify(password)
                raise InvalidError(
                    error="Invalid credentials", errors={"email": "Invalid credentials"}
                )

            if not self.hasher_service.verify(user_account.hashed_password, password):
                raise InvalidError(
                    error="Invalid credentials", errors={"email": "Invalid credentials"}
                )

            mfa_required = await self._check_mfa_requirements(user.id)

            if not mfa_required:
                session = await self._create_user_session(
                    user.id,
                    ip_address=ip_address,
                    device=device,
                    browser=browser,
                )
                return {
                    "mfa_required": False,
                    "session_uuid": session.uuid,
                }

            token = self._generate_temp_valid_details_token(
                user.id
            )
            return {
                "mfa_required": True,
                "temp_token": token,
            }

        except DomainError as de:
            await mediator.publish(
                UserInvalidLoginAttemptEvent(
                    user_id=user.id if user else None,
                    email=email,
                    reason=de.error,
                    attempt_at=datetime.now(UTC),
                    ip_address=ip_address,
                    device=device,
                    browser=browser,
                )
            )
            raise

    async def _check_mfa_requirements(self, user_id: int) -> bool:
        """
        Returns whether MFA is required for the user. The caller is responsible
        for short-circuiting session creation and issuing the MFA challenge when
        this returns True.
        """
        try:
            return await self.user_mfa_domain_service.is_mfa_required(user_id=user_id)
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                "Failed to check MFA requirements", internal_details=str(e)
            ) from e

    async def _create_user_session(
        self,
        user_id: int,
        ip_address: str,
        device: str,
        browser: str,
    ) -> UserSessionEntity:
        """
        Creates a new user session for the logged-in user.
        """
        try:
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
            total_sessions_len = len(total_sessions)
            if total_sessions_len >= config.MAX_AUTH_CONCURRENT_SESSIONS:
                raise InvalidError(
                    error=f"Maximum concurrent sessions exceeded. You have {total_sessions_len} active sessions.",
                    internal_details=f"User ID: {user_id}, Total Sessions: {total_sessions_len}",
                )
            return await self.user_session_domain_service.create_user_session(
                session_entity
            )
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                "Failed to create user session", internal_details=str(e)
            ) from e

    def _generate_temp_valid_details_token(
        self,
        user_id: int,
        expiry_minutes: int = 10,
    ) -> str:
        """
        Generates a temporary token to validate MFA details for the user.
        """
        try:
            token_data = {
                "user_id": user_id,
                "type": "mfa",
            }
            token, _ = self.token_service.generate_token(
                token_data, expiration_minutes=expiry_minutes
            )
            return token
        except Exception as e:
            raise ServerError(
                "Failed to generate MFA validation token", internal_details=str(e)
            ) from e
