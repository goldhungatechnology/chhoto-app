from src.modules.auth.domain.entities.user_account_entity import UserAccountEntity
from src.modules.auth.domain.repositories.user_account_repository import (
    IUserAccountRepository,
)
from src.shared.exceptions.base_exceptions import (
    CreateError,
    DomainError,
)


class UserAccountDomainService:
    """
    service class for user account domain logic
    """

    def __init__(self, repository: IUserAccountRepository):
        self.repository = repository

    async def create_user_account(
        self, account_entity: UserAccountEntity
    ) -> UserAccountEntity:
        """
        create user account
        """
        try:
            created_account = await self.repository.add(account_entity)
            return created_account
        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                "Failed to create user account", internal_details=str(e)
            ) from e

    async def get_user_account_by_user_id(
        self, user_id: int, type: str = "credentials", provider: str | None = None
    ) -> UserAccountEntity | None:
        """
        retrieves a user account by the associated user ID
        """
        try:
            criteria: dict = {"user_id": user_id, "type": type}
            if provider:
                criteria["provider"] = provider
            return await self.repository.get_by(**criteria)
        except Exception as e:
            raise CreateError(
                "Failed to retrieve user account by user ID", internal_details=str(e)
            ) from e

    async def update_user_account(
        self, account_entity: UserAccountEntity
    ) -> UserAccountEntity:
        """
        updates a user account
        """
        try:
            updated_account = await self.repository.update(account_entity)
            return updated_account
        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                "Failed to update user account", internal_details=str(e)
            ) from e
