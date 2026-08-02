from abc import ABC, abstractmethod
from src.modules.auth.domain.entities.user_mfa_recovery_entity import (
    UserMFARecoveryCodeEntity,
)
from src.shared.domain.repository.base_repository_interface import IBaseRepository


class IUserMFARecoveryRepository(IBaseRepository[UserMFARecoveryCodeEntity], ABC):
    """
    Interface for User MFA Recovery Code repository operations.
    """

    @abstractmethod
    async def add_many(
        self, entities: list[UserMFARecoveryCodeEntity]
    ) -> list[UserMFARecoveryCodeEntity]:
        """
        Add multiple recovery code entities.
        """
        pass

    @abstractmethod
    async def get_by_mfa_id(self, mfa_id: int) -> list[UserMFARecoveryCodeEntity]:
        """
        Get active recovery codes for an MFA ID.
        """
        pass
