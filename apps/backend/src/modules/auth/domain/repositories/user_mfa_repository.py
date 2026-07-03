from src.modules.auth.domain.entities.user_mfa_entity import UserMFAEntity
from src.shared.domain.repository.base_repository_interface import IBaseRepository


class IUserMFARepository(IBaseRepository[UserMFAEntity]):
    """
    Interface for the User MFA repository.
    """
