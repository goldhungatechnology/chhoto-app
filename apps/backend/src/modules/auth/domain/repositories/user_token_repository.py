from src.modules.auth.domain.entities.user_token_entity import UserTokenEntity
from src.shared.domain.repository.base_repository_interface import IBaseRepository


class IUserTokenRepository(IBaseRepository[UserTokenEntity]):
    """
    Interface for the User Token repository.
    """
