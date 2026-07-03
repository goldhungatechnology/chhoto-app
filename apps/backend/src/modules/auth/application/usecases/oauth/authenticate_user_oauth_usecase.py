from datetime import UTC, datetime
from typing import Literal

from fastapi.requests import Request

from src.core.config.settings import config
from src.modules.auth.domain.entities.user_account_entity import UserAccountEntity
from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.entities.user_session_entity import UserSessionEntity
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
from src.modules.auth.infrastructure.oauth.interface.oauth_provider_interface import (
    OAuthUserInfo,
)
from src.shared.exceptions.base_exceptions import DomainError, InvalidError, ServerError
from src.shared.infrastructure.token.token_service import TokenService


class AuthenticatUserOAuthUseCase:
    """
    Use case for authenticating a user using OAuth.
    """

    def __init__(
        self,
        user_domain_service: UserDomainService,
        user_account_domain_service: UserAccountDomainService,
        user_session_domain_service: UserSessionDomainService,
        user_mfa_domain_service: UserMFADomainService,
        token_service: TokenService,
    ):
        self.user_domain_service = user_domain_service
        self.user_account_domain_service = user_account_domain_service
        self.user_mfa_domain_service = user_mfa_domain_service
        self.user_session_domain_service = user_session_domain_service
        self.token_service = token_service

    async def execute(
        self, provider: Literal["google"], request: Request
    ) -> tuple[str, dict]:
        """
        Authenticate a user using the specified OAuth provider.
        """

        user_info = await self._get_user_info(provider, request)
        if not user_info or not user_info.email:
            raise ServerError("Failed to retrieve user information from OAuth provider")

        # An unverified provider email must never be trusted: account linking
        # below matches existing local accounts purely by email, so accepting an
        # unverified address would let an attacker take over a victim's account.
        if not user_info.email_verified:
            raise InvalidError(
                error="Your email address is not verified with the provider.",
                internal_details=f"Unverified OAuth email for provider={provider}",
            )

        already_user = await self._find_user_by_email(user_info.email)
        if already_user:
            login_data = await self._handle_login_for_existing_user(
                already_user, provider, user_info
            )
            # When MFA is required there is no session yet — only a temp token.
            # Signal a distinct status so the caller does not look for a
            # session_uuid (which would raise KeyError).
            if login_data.get("mfa_required"):
                return ("mfa", login_data)
            return ("login", login_data)

        new_user = await self._create_user_from_oauth_info(user_info, provider)
        return ("signup", new_user)

    async def _get_user_info(self, provider, request: Request):
        """
        Get user information from the specified OAuth provider.
        """
        from src.modules.auth.infrastructure.oauth.oauth_factory import OAuthFactory

        oauth_provider = OAuthFactory.get_provider(provider)

        return await oauth_provider.get_user(request)

    async def _find_user_by_email(self, email: str):
        """
        Find a user in the database by their email address.
        """
        return await self.user_domain_service.get_user_by_email(email)

    async def _handle_user_account_creation(self, user_id: int, provider: str):
        """
        Handle the creation of a user account for the specified provider.
        """
        user_account = UserAccountEntity(
            type="oauth",
            user_id=user_id,
            provider=provider,
        )
        return await self.user_account_domain_service.create_user_account(user_account)

    async def _handle_login_for_existing_user(
        self, user, provider, user_info: OAuthUserInfo
    ):
        """
        Handle the login process for an existing user.
        1. Check if the user already has an account for this provider. If not, create one.
        2. Check if the user has MFA enabled. If so, trigger the MFA flow.
        """
        user_account = (
            await self.user_account_domain_service.get_user_account_by_user_id(
                user.id, type="oauth", provider=provider
            )
        )
        if not user_account:
            # If the user exists but doesn't have an account for this provider, create one
            await self._handle_user_account_creation(user.id, provider)

        mfa_required = await self._check_mfa_requirements(user.id)
        if not mfa_required:
            session = await self._create_user_session(
                user.id,
                ip_address=user_info.ip_address,
                device=user_info.device,
                browser=user_info.browser,
            )
            return {
                "mfa_required": False,
                "session_uuid": session.uuid,
            }

        token = self._generate_temp_valid_details_token(user.id)
        return {
            "mfa_required": True,
            "temp_token": token,
        }

    async def _check_mfa_requirements(self, user_id: int) -> bool:
        """
        Returns whether MFA is required for the user. The caller short-circuits
        session creation and issues the MFA challenge when this returns True.
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
        ip_address: str | None = None,
        device: str | None = None,
        browser: str | None = None,
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
        self, user_id: int, expiry_minutes: int = 10
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

    async def _create_user_from_oauth_info(
        self, user_info: OAuthUserInfo, provider: str
    ):
        """
        Creates a new user in the system based on the information retrieved from the OAuth provider.
        """
        try:
            user = UserEntity(
                username=UserEntity.generate_username(user_info.email),
                email=user_info.email.lower(),
                avatar_bg=UserEntity.generate_random_avatar_bg(),
                avatar=user_info.avatar_url,
                email_verified_at=datetime.now(UTC),
                status="active",
            )
            new_user = await self.user_domain_service.create_user(user)
            if not new_user.id:
                raise ServerError(error="Failed to create user")

            ## account handling — store the real provider so the login lookup
            ## (which queries by provider) matches and we don't create a
            ## duplicate account on every subsequent login.
            _ = await self._handle_user_account_creation(new_user.id, provider=provider)
            session = await self._create_user_session(
                new_user.id,
                ip_address=user_info.ip_address,
                device=user_info.device,
                browser=user_info.browser,
            )

            return {
                "user_id": new_user.id,
                "email": new_user.email,
                "username": new_user.username,
                "session_uuid": session.uuid,
                "session_expires_at": session.expires_at.isoformat(),
            }

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                "Failed to create user from OAuth information", internal_details=str(e)
            ) from e
