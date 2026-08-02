from datetime import UTC, datetime

from src.modules.auth.domain.entities.user_mfa_entity import UserMFAEntity
from src.modules.auth.domain.repositories.user_mfa_repository import IUserMFARepository
from src.shared.exceptions.base_exceptions import (
    CreateError,
    DomainError,
    ServerError,
    UpdateError,
)


class UserMFADomainService:
    """
    service class for user mfa domain logic
    """

    def __init__(self, repository: IUserMFARepository):
        self.repository = repository

    async def create_user_mfa(self, mfa_entity: UserMFAEntity) -> UserMFAEntity:
        """
        create user mfa or update existing unverified mfa setup
        """
        try:
            already_exists = await self.get_user_mfa_by_user_id(mfa_entity.user_id)
            if already_exists:
                if already_exists.verified_at is not None:
                    raise CreateError(
                        "MFA is already enabled for this account",
                        internal_details=f"User ID: {mfa_entity.user_id}",
                    )
                # Existing setup is unverified; update secret and auth_url to allow retry/re-setup
                already_exists.secret = mfa_entity.secret
                already_exists.auth_url = mfa_entity.auth_url
                already_exists.mark_updated()
                return await self.repository.update(already_exists)

            created_mfa = await self.repository.add(mfa_entity)
            return created_mfa
        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                "Failed to create user MFA", internal_details=str(e)
            ) from e

    async def get_user_mfa_by_user_id(self, user_id: int):
        """
        retrieves a user mfa by the associated user ID
        """
        try:
            return await self.repository.get_by(user_id=user_id, revoked_at=None)
        except Exception as e:
            raise CreateError(
                "Failed to retrieve user MFA by user ID", internal_details=str(e)
            ) from e

    async def get_verified_user_mfa_by_user_id(self, user_id: int):
        """
        retrieves a verified (confirmed) user mfa by the associated user ID
        """
        try:
            mfa = await self.repository.get_by(user_id=user_id, revoked_at=None)
            if mfa and mfa.verified_at is not None:
                return mfa
            return None
        except Exception as e:
            raise CreateError(
                "Failed to retrieve verified user MFA by user ID",
                internal_details=str(e),
            ) from e

    async def is_mfa_required(self, user_id: int) -> bool:
        """
        checks if MFA is required for a given user ID
        (only returns True if MFA is both present and verified)
        """
        try:
            mfa = await self.get_verified_user_mfa_by_user_id(user_id)
            return mfa is not None
        except Exception as e:
            raise ServerError(
                "Failed to check if MFA is required", internal_details=str(e)
            ) from e

    async def confirm_user_mfa(self, mfa_entity: UserMFAEntity) -> UserMFAEntity:
        """
        confirms (verifies) a user MFA by setting the verified_at timestamp
        """
        try:
            mfa_entity.verified_at = datetime.now(UTC)
            mfa_entity.mark_updated()
            return await self.repository.update(mfa_entity)
        except Exception as e:
            raise UpdateError(
                "Failed to confirm user MFA", internal_details=str(e)
            ) from e

    async def disable_user_mfa(self, mfa_entity: UserMFAEntity) -> UserMFAEntity:
        """
        disables (revokes) a user MFA by setting the revoked_at timestamp
        """
        try:
            mfa_entity.revoked_at = datetime.now(UTC)
            mfa_entity.mark_updated()
            return await self.repository.update(mfa_entity)
        except Exception as e:
            raise UpdateError(
                "Failed to disable user MFA", internal_details=str(e)
            ) from e
