from abc import ABC, abstractmethod
from typing import Generic, TypeVar

TMessage = TypeVar("TMessage")


class INotification(ABC, Generic[TMessage]):
    """
    interfaces for notification
    """

    @abstractmethod
    async def send(self, message: TMessage):
        """
        send notification to recipient with message
        """
        raise NotImplementedError
