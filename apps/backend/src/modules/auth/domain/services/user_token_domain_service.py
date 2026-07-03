from typing import Literal
from datetime import UTC, datetime, timedelta
from src.core.config.settings import config
from src.modules.auth.domain.entities.user_token_entity import UserTokenEntity
from src.modules.auth.domain.repositories.user_token_repository import (
    IUserTokenRepository,
)
from src.shared.infrastructure.hasher.hasher import HasherService
from src.shared.infrastructure.token.token_service import TokenService


class UserTokenDomainService:
    """
    UserTokenDomainService is responsible for handling the token logic
    """

    def __init__(
        self,
        repository: IUserTokenRepository,
        token_service: TokenService,
        hasher: HasherService,
    ):
        self.repository = repository
        self.token_service = token_service
        self.hasher = hasher

    async def create_user_token(
        self,
        user_id: int,
        type: Literal["email_verification", "forgot-password"],
        expiry_minutes: int = 60 * 24,
    ) -> str:
        """
        Creates a new user token for the specified user and type.
        """

        # Password-reset tokens are the sole credential carried in an emailed
        # link and are never typed by a human, so they must be high-entropy.
        # Email-verification codes are short OTPs entered by the user.
        if type == "forgot-password":
            random_token = self.token_service.secure_token()
        else:
            random_token = self.token_service.random_token(digit=config.TOKEN_DIGIT)
        expires_at = datetime.now(UTC) + timedelta(minutes=expiry_minutes)
        token_hash = self.hasher.deterministic_hash(random_token)

        new_token = UserTokenEntity(
            user_id=user_id,
            type=type,
            expires_at=expires_at,
            token_hash=token_hash,
        )
        await self.repository.add(new_token, audit=False)

        return random_token

    async def verify_user_token(
        self,
        type: Literal["email_verification", "forgot-password"],
        user_id: int,
        token: str,
    ) -> tuple[bool, UserTokenEntity | None]:
        """
        verify user token
        """
        user_token = await self.repository.get_by(
            type=type,
            user_id=user_id,
            expires_at__gt=datetime.now(UTC),
            used_at=None,
            token_hash=self.hasher.deterministic_hash(token),
        )
        if not user_token:
            return (False, None)

        return (True, user_token)

    async def list_user_tokens(
        self, user_id: int, type: Literal["email_verification"] | None = None
    ) -> list[UserTokenEntity]:
        """
        List all tokens for a user, optionally filtered by type.
        """
        filters = {
            "user_id": user_id,
            "expires_at__gt": datetime.now(UTC),
            "used_at": None,
        }
        if type:
            filters["type"] = type

        return await self.repository.filter(**filters)

    async def get_user_token_by_token(
        self, token: str, type: Literal["email_verification", "forgot-password"]
    ) -> UserTokenEntity | None:
        """Get a user token by its token value and type."""
        return await self.repository.get_by(
            type=type,
            expires_at__gt=datetime.now(UTC),
            used_at=None,
            token_hash=self.hasher.deterministic_hash(token),
        )

    async def mark_token_as_used(self, token: UserTokenEntity):
        """
        Mark a token as used by setting the used_at timestamp to the current time.
        """
        token.mark_as_used()
        await self.repository.update(token, audit=False)

    async def invalidate_active_tokens(
        self,
        user_id: int,
        type: Literal["email_verification", "forgot-password"],
    ) -> int:
        """
        Consume every still-valid, unused token of the given type for the user.

        Used before issuing a new token so that only one credential is ever live
        at a time (e.g. requesting a second password-reset link must invalidate
        the first, narrowing the attack window).
        """
        active_tokens = await self.repository.filter(
            user_id=user_id,
            type=type,
            expires_at__gt=datetime.now(UTC),
            used_at=None,
        )
        for token in active_tokens:
            await self.mark_token_as_used(token)
        return len(active_tokens)
