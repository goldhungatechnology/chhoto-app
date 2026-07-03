from datetime import UTC, datetime
from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.events.auth_domain_events import UserUpdatedEvent
from src.modules.auth.domain.interfaces.email_validator_interface import (
    IEmailDomainValidator,
)
from src.modules.auth.domain.repositories.user_repository import IUserRepository
from src.shared.exceptions.base_exceptions import (
    ConflictError,
    CreateError,
    DomainError,
    InvalidError,
)


class UserDomainService:
    """
    service class for user domain logic
    """

    def __init__(
        self, repository: IUserRepository, email_validator: IEmailDomainValidator
    ):
        self.repository = repository
        self.email_validator = email_validator

    async def create_user(self, user_entity: UserEntity) -> UserEntity:
        """
        creates a new user
        """
        try:
            await self._ensure_email_unique(user_entity.email)
            await self._ensure_username_unique(user_entity.username)
            await self._ensure_not_temporary_email(user_entity)
            await self._ensure_email_valid(user_entity.email)

            return await self.repository.add(user_entity)

        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to create user", internal_details=str(e)
            ) from e

    async def get_user_by_id(self, user_id: int) -> UserEntity | None:
        """
        retrieves a user by its ID
        """
        try:
            user = await self.repository.get_by_id(user_id)
            if not user or not user.is_active():
                return None
            return user
        except Exception as e:
            raise CreateError(
                error="Failed to retrieve user", internal_details=str(e)
            ) from e

    async def get_user_by_uuid(self, user_uuid: str) -> UserEntity | None:
        """
        retrieves a user by its UUID
        """
        try:
            user = await self.repository.get_by_uuid(user_uuid)
            if not user or not user.is_active():
                return None
            return user
        except Exception as e:
            raise CreateError(
                error="Failed to retrieve user", internal_details=str(e)
            ) from e

    async def get_user_by_email(self, email: str) -> UserEntity | None:
        """
        retrieves a user by its email
        """
        try:
            user = await self.repository.get_by(email=email)
            if not user or not user.is_active():
                return None
            return user
        except Exception as e:
            raise CreateError(
                error="Failed to retrieve user", internal_details=str(e)
            ) from e

    async def get_users_by_uuids(self, user_uuids: list[str]) -> list[UserEntity]:
        """
        retrieves active users for a list of UUIDs in a single query.
        Empty input short-circuits to avoid an empty IN-clause.
        """
        try:
            if not user_uuids:
                return []
            users = await self.repository.filter(uuid__in=user_uuids)
            return [user for user in users if user.is_active()]
        except Exception as e:
            raise CreateError(
                error="Failed to retrieve users", internal_details=str(e)
            ) from e

    async def mark_onboarded(
        self, user_id: int, full_name: str | None = None
    ) -> UserEntity:
        """
        Marks the user as onboarded by setting the onboarded field to True.
        Optionally updates the user's full name as part of onboarding.
        """
        try:
            user = await self.repository.get_by_id(user_id)
            if not user:
                raise InvalidError(error="User not found")

            user.complete_onboarding()
            if full_name:
                user.change_full_name(full_name)
            return await self.update_user(user)
        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to mark user as onboarded", internal_details=str(e)
            ) from e

    async def mark_email_verified(self, user_id: int) -> UserEntity:
        """
        Marks the user's email as verified by setting the email_verified field to True.
        """
        try:
            user = await self.repository.get_by_id(user_id)
            if not user:
                raise InvalidError(error="User not found")

            user.email_verified_at = datetime.now(UTC)
            return await self.update_user(user)
        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to mark email as verified", internal_details=str(e)
            ) from e

    async def update_user(self, user_entity: UserEntity) -> UserEntity:
        """
        updates an existing user
        """
        try:
            user = await self.repository.update(user_entity, audit=False)
            if not user.id:
                raise InvalidError(error="User not found")

            user.add_event(UserUpdatedEvent(user_id=user.id))
            return user
        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to update user", internal_details=str(e)
            ) from e

    async def _ensure_email_unique(self, email: str) -> None:
        """
        Checks if a user with the same email already exists. If so, raises a ConflictError.
        """
        existing_user = await self.repository.get_by(email=email)
        if existing_user:
            raise ConflictError(
                error="User with this email already exists",
                errors={"email": "A user with this email already exists"},
            )

    async def _ensure_username_unique(self, username: str) -> None:
        """
        Checks if a user with the same username already exists. If so, raises a ConflictError.
        """
        existing_user = await self.repository.get_by(username=username)
        if existing_user:
            raise ConflictError(error="User with this username already exists")

    async def _ensure_not_temporary_email(self, user_entity: UserEntity) -> None:
        """
        Checks if the email is from a temporary email domain. If so, raises an InvalidError.
        """
        if user_entity.is_temporary_email():
            raise InvalidError(
                errors={"email": "Temporary email addresses are not allowed"},
            )

    async def _ensure_email_valid(self, email: str) -> None:
        """
        Validates the email using the provided email validator. If the email domain is invalid, raises an InvalidError.
        """
        if (await self.email_validator.domain_exists(email)) is False:
            raise InvalidError(
                errors={"email": "Email domain is invalid or does not exist"},
            )
