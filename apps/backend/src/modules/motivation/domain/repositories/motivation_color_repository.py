from abc import abstractmethod

from src.modules.motivation.domain.entities.motivation_color_entity import (
    MotivationColorEntity,
)
from src.shared.domain.repository.base_repository_interface import IBaseRepository


class IMotivationColorRepository(IBaseRepository[MotivationColorEntity]):
    """
    Interface for motivation color repository.
    """

    @abstractmethod
    async def list_by_config_id(
        self,
        config_id: int,
    ) -> list[MotivationColorEntity]:
        """
        List motivation colors by config id.
        """
        pass

    @abstractmethod
    async def delete_by_id(
        self,
        color_id: int,
    ) -> None:
        """
        Delete motivation color by id.
        """
        pass
