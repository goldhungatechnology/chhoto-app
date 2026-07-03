from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.auth_container import get_auth_container
from src.modules.auth.domain.entities.user_account_entity import UserAccountEntity
from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.entities.user_session_entity import UserSessionEntity
from src.modules.auth.domain.ports.user.user_provisioner import (
    ProvisionedUser,
    UserProvisioner,
)
from src.modules.auth.domain.services.user_account_domain_service import (
    UserAccountDomainService,
)
from src.modules.auth.domain.services.user_domain_service import UserDomainService
from src.modules.auth.domain.services.user_session_domain_service import (
    UserSessionDomainService,
)
from src.shared.exceptions.base_exceptions import ServerError
from src.shared.infrastructure.hasher.hasher import HasherService


class UserProvisionerImpl(UserProvisioner):
    """
    Bound to the caller's session so creation participates in the surrounding
    transaction. Differs from the normal signup path in three ways:
      - email is pre-marked as verified (no token round-trip)
      - is_onboarded is set to True (the inviting org acts as the onboarding)
      - emits no UserCreatedEvent (we do NOT want the welcome / email-
        verification listeners to fire for invited users)
    """

    def __init__(
        self,
        user_domain_service: UserDomainService,
        user_account_domain_service: UserAccountDomainService,
        user_session_domain_service: UserSessionDomainService,
        hasher_service: HasherService,
    ):
        self.user_domain_service = user_domain_service
        self.user_account_domain_service = user_account_domain_service
        self.user_session_domain_service = user_session_domain_service
        self.hasher_service = hasher_service

    async def provision_invited_user(
        self,
        *,
        email: str,
        password: str,
        full_name: str | None = None,
    ) -> ProvisionedUser:
        normalized_email = email.strip().lower()

        user = UserEntity(
            username=UserEntity.generate_username(normalized_email),
            email=normalized_email,
            full_name=full_name,
            avatar_bg=UserEntity.generate_random_avatar_bg(),
            status="active",
            is_onboarded=True,
            email_verified_at=datetime.now(UTC),
        )

        new_user = await self.user_domain_service.create_user(user)
        if not new_user.id:
            raise ServerError(error="Failed to provision invited user")

        account = UserAccountEntity(
            type="credentials",
            user_id=new_user.id,
            hashed_password=self.hasher_service.hash(password),
        )
        await self.user_account_domain_service.create_user_account(account)

        session_entity = UserSessionEntity(
            user_id=new_user.id, expires_at=UserSessionEntity.set_expiration()
        )
        new_session = await self.user_session_domain_service.create_user_session(
            session_entity
        )

        return ProvisionedUser(
            user_id=new_user.id,
            user_uuid=new_user.uuid,
            email=new_user.email,
            username=new_user.username,
            session_uuid=new_session.uuid,
            session_expires_at=new_session.expires_at,
        )


def get_user_provisioner(session: AsyncSession) -> UserProvisionerImpl:
    """
    Build a provisioner bound to the caller's session. Reuses the auth
    container so we don't duplicate wiring for hasher / domain services.
    """
    container = get_auth_container(session)
    return UserProvisionerImpl(
        user_domain_service=container.user_domain_service(),
        user_account_domain_service=container.user_account_domain_service(),
        user_session_domain_service=container.user_session_domain_service(),
        hasher_service=container.hasher_service(),
    )
