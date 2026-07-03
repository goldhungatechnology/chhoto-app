from abc import abstractmethod

from src.modules.motivation.domain.entities.daily_motivation_config_entity import (
    DailyMotivationConfigEntity,
)
from src.shared.domain.repository.base_repository_interface import IBaseRepository


class IDailyMotivationConfigRepository(IBaseRepository[DailyMotivationConfigEntity]):
    """
    Interface for daily motivation config repository.
    """

    @abstractmethod
    async def get_by_organization_id(
        self, organization_id: int
    ) -> DailyMotivationConfigEntity | None:
        """
        Get motivation config by organization id.
        """
        pass
