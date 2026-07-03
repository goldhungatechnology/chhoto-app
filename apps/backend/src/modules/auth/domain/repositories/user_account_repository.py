from src.modules.auth.domain.entities.user_account_entity import UserAccountEntity
from src.shared.domain.repository.base_repository_interface import IBaseRepository


class IUserAccountRepository(IBaseRepository[UserAccountEntity]):
    """
    Interface for the User Accountrepository.
    """
