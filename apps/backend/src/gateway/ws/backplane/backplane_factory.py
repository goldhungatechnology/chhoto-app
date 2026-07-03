from typing import Literal

from src.core.config.settings import config
from src.gateway.ws.backplane.interface import IBackplane


class BackPlanFactory:
    """
    Factory for creating backplane instances.
    """

    @classmethod
    def create_backplane(cls, backplane_type: Literal["redis"]) -> IBackplane:
        """
        Create a backplane instance based on the specified type. Currently, only "redis" is supported, which creates an instance of RedisBackplane. The method can be extended in the future to support additional backplane types by adding new cases to the conditional logic.
        """

        match backplane_type:
            case "redis":
                from src.gateway.ws.backplane.redis_backplane import RedisBackplane

                return RedisBackplane(config.REDIS_URL)
            case _:
                raise ValueError(f"Unsupported backplane type: {backplane_type}")
