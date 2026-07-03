from src.modules.auth.domain.entities.user_entity import UserEntity
from src.shared.domain.repository.base_repository_interface import IBaseRepository


class IUserRepository(IBaseRepository[UserEntity]):
    """
    Interface for the User repository.
    """
